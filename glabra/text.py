# The MIT License (MIT)
#
# Copyright (c) 2015 Christofer Hedbrandh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'Christofer Hedbrandh (chedbrandh@gmail.com)'
__copyright__ = 'Copyright (c) 2015 Christofer Hedbrandh'

import re
import random
import codecs

from glabra import buckets
from glabra import create
from glabra import analyze

# number of bytes to read from file at a time
_BUFFER_SIZE = 2**20

# regex for parsing bounds strings
BOUNDS_REGEX = re.compile(r"^(\d+):(100|\d\d?),(100|\d\d?)$")

class TextGenerator(object):
  """Helper for creating new words/sentences from training data.

  Provides utility funcitons for generating words and sentences.

  Allowed text lengths are pulled from the training data in a
  SequenceAnalyzer. Only texts of lenghts already seen in the training data
  can be generated. (Texts shorter than the minimum allowed are also excluded.)

  A post processing function is typically useful for sentences and allows for
  turning a list of words into an actual sentence string.
  """

  def __init__(self, bounds, sequence_analyzer, post_processing_fun=None):
    """Builds sequence creators for all (legal) lengths in the training data.

    Sequence creators are created from a SequenceAnalyzer and some bounds. The
    bounds specify which n-grams from the training data in the
    SequenceAnalyzer that can be used for generating text. (See buckets
    and analyze for more details.)

    Args:
      bounds: Bounds that n-grams must be within.
      sequence_analyzer: SequenceAnalyzer to get n-grams from.
      post_processing_fun: Function to apply to the generated sequence.
    """

    # set sequences analyzer and post processing function
    self._sa = sequence_analyzer
    self._post_processing_fun = post_processing_fun

    # get the set of n-grams, leading and trailing, used for text creation
    self._ngrams = buckets.get_ngrams(self._sa, bounds)
    self._ngrams_leading = buckets.get_ngrams_leading(self._sa, bounds)
    self._ngrams_trailing = buckets.get_ngrams_trailing(self._sa, bounds)

    # minimum allowed length is one with only one middle vertex/n-gram
    self._min_len = create.get_len_single_middle_vertex(
        len(self._ngrams_leading[0]), len(self._ngrams[0]), len(self._ngrams_trailing[0]))

    # dictionary from sequence length to sequence creator
    self._seq_creator_dict = {}

    # dictionary from sequence length to sequence frequency
    self._seq_freq_dict = {}

    # populate sequence dictionaries
    self._build_sequence_dicts()

  def is_empty(self):
    """If no text can be created from the given bounds and analyzers."""
    return len(self._seq_creator_dict) == 0

  def get_all_texts(self, unique=False):
    """Generate all texts of all lengths appearing in the training data.

    Args:
      unique: Texts appearing in the training data will not filtered out.

    Returns:
      All possible texts.
    """
    # for all lengths generate all texts
    for len_seq in sorted(self._seq_creator_dict.keys()):
      for post_processed_text in self._get_all_texts_of_length(len_seq, unique):
        yield post_processed_text

  def get_random_texts(self, num_requested, unique=False):
    """Generate some number of random texts of random lengths.

    Only texts of lenghts that appear in the training data will be returned.

    Args:
      num_requested: Number of random random texts to generate.
      unique: Texts appearing in the training data, and texts already generated
        during the method call, will be filtered out. This means that fewer
        than num_requested number of texts may be returned.

    Returns:
      Some number of random texts of random lengths.
    """
    # return an empty generator if no texts can be generated
    if self.is_empty():
      return

    # set of texts that should not be returned
    filter_set = set(self._sa.get_sequences()) if unique else set()

    # generate some number of texts
    for _ in range(num_requested):
      len_seq = self._get_random_text_length()
      text = self._seq_creator_dict[len_seq].get_random_sequence()
      # maybe filter out already seen texts
      if text not in filter_set:
        if unique:
          filter_set.add(text)
        yield self._post_process_text(text)

  def _get_all_texts_of_length(self, text_length, unique=False):
    """Generate all texts of some length.

    If the specified length does not appear in the training data then no texts
    will be generated.

    Args:
      text_length: The length of the text to create.
      unique: Texts appearing in the training data will not be returned.

    Returns:
      Texts of a given length.
    """
    # return an empty generator if text length has no sequence creator
    if text_length not in self._seq_creator_dict:
      return

    # set of texts that should not be returned
    filter_set = set(self._sa.get_sequences()) if unique else set()

    # generate all texts of some lenght
    for text in self._seq_creator_dict[text_length].get_all_sequences():
      if text not in filter_set:
        yield self._post_process_text(text)

  def _build_sequence_dicts(self):
    """Build all sequence dictionaries.

    Populates self._seq_creator_dict with sequence lenghts (keys) and sequence
    creators (values), and self._seq_freq_dict with sequence lenghts (keys) and
    sequence frequenceis (values).
    """
    for (len_seq, seq_freq) in self._sa.get_sequence_length_freq_dict().items():
      # ignore sequence lengths that are too short
      if len_seq < self._min_len:
        continue
      # create sequence creator for length len_seq
      seq_creator = create.SequenceCreator(
        len_seq, self._ngrams_leading, self._ngrams, self._ngrams_trailing)
      # ignore sequence lengths that that can't create sequences
      if seq_creator.is_disconnected():
        continue
      # populate sequence dictionaries
      self._seq_creator_dict[len_seq] = seq_creator
      self._seq_freq_dict[len_seq] = seq_freq

  def _get_random_text_length(self):
    """Get a random text length based on the data in the sequences analyzer."""
    # randomly pick a number between zero and the total frequency
    total_freq = sum(self._seq_freq_dict.values())
    rand_cum_freq = random.random() * total_freq
    current_cum_freq = 0
    # iterate through all text lengths until the randomly selected point is reached
    for (len_text, freq) in self._seq_freq_dict.items():
      if rand_cum_freq < current_cum_freq + freq:
        return len_text
      else:
        current_cum_freq += freq

  def _post_process_text(self, text):
    """Apply the post processing function to the created text."""
    if self._post_processing_fun == None:
      return text
    return self._post_processing_fun(text)

def get_sequence_analyzer(filename, sequence_delimiter_pattern,
    element_delimiter_pattern=None, frequency_grouping_pattern=None):
  """Parses and analyzes a text file.

  If the intention is to generate words from a text file, "sequences" in this
  context are words, and "elements" are letters. A sequence delimiter would
  therefore typically be white spaces and other non-alphanumeric characters.

  If the intention is to generate sentences, "sequences" in this context are
  sentences and "elements" are be words. A sequence delimiter would typically
  be periods or line breaks, and an element delimiter would typically be white
  spaces and other non-alphanumeric characters.

  If the text file contains frequencies a frequency pattern must be provided in
  order to parse the frequency. The pattern is expected to contain two groups;
  the first group being the sequence and the second the frequency.

  E.g.

  File content:
  "First shalt thou take out the Holy Pin. Then shalt thou count
  to three, no more, no less. Three shall be the number thou
  shalt count, and the number of the counting shall be three."

  sequence_delimiter_pattern: "."
  element_delimiter_pattern: "\\s|\\,|\\n"

  E.g.

  File content:
  "Smith:2376207
  Johnson:1857160
  Williams:1534042
  Brown:1380145
  Jones:1362755"

  sequence_delimiter_pattern: "\\n"
  frequency_grouping_pattern: "(.+):(\\d+)"

  Args:
    filename: Name of file to parse.
    sequence_delimiter_pattern: Pattern for separating sequences.
    element_delimiter_pattern: Pattern for separating sequence elements.
    frequency_grouping_pattern: Pattern for finding sequence frequency.

  Returns:
    SequenceAnalyzer of text file.
  """
  # compile delimiter patterns
  seq_delim = re.compile(sequence_delimiter_pattern)
  elem_delim = None if element_delimiter_pattern is None \
      else re.compile(element_delimiter_pattern)
  freq_grouping = None if frequency_grouping_pattern is None \
      else re.compile(frequency_grouping_pattern)

  # tuples of sequences and their frequencies
  seq_freqs = []

  # read, parse, and analyze the specified file
  with codecs.open(filename, 'r', encoding='utf8') as f:

    # parse file in to sequences
    seqs = _split_file(f, seq_delim)

    # iterate through all sequence and potentially parse them further
    for seq in seqs:
      freq = 1.0

      # if file contains a frequency pattern
      if not freq_grouping == None:
        matching = freq_grouping.match(seq)
        # ignore sequence if pattern matching fails
        if matching == None:
          continue
        seq = matching.group(1)
        freq = float(matching.group(2))

      # parse sequence if element delimiter is specified
      if not elem_delim == None:
        seq = _parse_seq(seq, elem_delim)

      # add sequence with its frequency to the list
      seq_freqs.append((seq, freq))

  # raise error if no sequences were retrieved from the file
  if len(seq_freqs) == 0:
    raise ValueError("File %s provided no data." % filename)

  # return an analyzer of all sequences with their frequencies
  return analyze.SequenceAnalyzer(seq_freqs)

def parse_bounds(str_bounds):
  """Parse bound strings.

  A bound string is expected to be on the format:
  <NGRAM_LENGTH>:<LOWER_BOUND>,<UPPER_BOUND>

  E.g. ["3:0,100", "5:25,75"]

  n-gram length must be a positive integer and
  0 <= LOWER_BOUND <= UPPER_BOUND <= 100

  Args:
    Bound strings to be parsed.

  Returns:
    A parsed bounds dictionary on format {LEN:(LB,UB)}.
  """
  result = {}
  for str_bound in str_bounds:
    m = BOUNDS_REGEX.match(str_bound)
    # raise exception if string could not be parsed
    if m is None:
      raise ValueError("Bound string %s does not match expectd pattern %s." %
        (str_bound, BOUNDS_REGEX.pattern))
    (len_ng, lb, ub) = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # raise exception if not lower bound < upper bound
    if not lb < ub:
      raise ValueError("Lower bound %s is not less than upper bound %s." %
        (lb, ub))
    # add bound to bounds dictionary
    result[len_ng] = (lb, ub)
  return result

def _parse_seq(seq, elem_delim):
  """Parses a sequence with a delimiter pattern."""
  elems = elem_delim.split(seq)
  elems = filter(None, elems)
  return tuple(elems)

def _split_file(f, delim):
  """Parses a file an returns sequences given a delimiter."""
  # sequence part that carries over from last read
  seq_buffer = ""
  while True:
    text = f.read(_BUFFER_SIZE)
    # if reached end of file, flush buffer
    if text == "":
      if not seq_buffer == "":
        yield seq_buffer
      break
    # split read text by delimiter
    seqs = delim.split(text)
    if len(seqs) > 1:
      # add what was left in the buffer from previous iteration
      seqs[0] = seq_buffer + seqs[0]
      seq_buffer = ""
      for seq in seqs[:-1]:
        if seq is "":
          continue
        yield seq
    seq_buffer += seqs[-1]
