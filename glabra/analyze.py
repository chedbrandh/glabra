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

import copy

class SequenceAnalyzer(object):
  """Provides analytics for some given sequences.

  Sequences and its n-grams are analyzed by their frequencies. The
  n-grams are analyzed separately by leading and trailing n-grams,
  and by all n-grams for a sequence.

  Analytics provided are n-grams' frequencies and percentiles.

  Frequencies of sequencies and n-grams of an instance can be modified
  by using the + and * operators. Two instances can be added with the +
  operator, and frequencies of an instance can be multiplied by a number with
  the * operator.

  Glossary:
    Leading n-gram: An n-gram that shares its first element with the
    first element of the sequence it was derived from.

    Trailing n-gram: An n-gram that shares its last element with the
    last element of the sequence it was derived from.
  """

  def __init__(self, sequences_frequencies):
    """Sequences are added for analysis at initialization.

    Args:
      sequences_frequencies: Tuples of (sequence, frequency) where
        frequency indicates the frequency of the sequence.
    """
    if len(sequences_frequencies) == 0:
      raise ValueError("Must provide some sequences.")

    # {len_ng:{ng:freq}}
    self._freq_dict = {}
    self._freq_dict_leading = {}
    self._freq_dict_trailing = {}

    # {len_ng:total_freq}
    # note that leading and trailing total_freq_dicts will be identical
    self._total_freq_dict = {}
    self._total_freq_dict_leading = {}
    self._total_freq_dict_trailing = {}

    # {len_seq:total_freq}
    self._seq_len_dict = {}
    # {seq:total_freq}
    self._seq_freq_dict = {}

    # add sequences and n-grams
    self._add_seqs(sequences_frequencies)

  def _add_seqs(self, seqs_freqs):
    """Add all sequences with assosiated frequency.

    For every sequence also add every possible n-gram, leading
    n-gram, and trailing n-gram.

    Args:
      seqs_freqs: Tuples of (sequence, frequency).
    """
    for seq, freq in seqs_freqs:
      if freq <= 0:
        raise ValueError("Sequence frequency must be greater than zero.")
      # set self._seq_freq_dict
      self._seq_freq_dict[seq] = self._seq_freq_dict.get(seq, 0) + freq
      # set self._seq_len_dict
      self._seq_len_dict[len(seq)] = self._seq_len_dict.get(len(seq), 0) + freq
      # for all n-gram lengths
      for len_ng in range(1, len(seq) + 1):
        # set self._freq_dict_leading and self._total_freq_dict_leading
        ng = seq[:len_ng]
        d = self._freq_dict_leading.setdefault(len_ng, {})
        d[ng] = d.get(ng, 0) + freq
        self._total_freq_dict_leading[len_ng] = \
            self._total_freq_dict_leading.get(len_ng, 0) + freq
        # set self._freq_dict_trailing and self._total_freq_dict_trailing
        ng = seq[-len_ng:]
        d = self._freq_dict_trailing.setdefault(len_ng, {})
        d[ng] = d.get(ng, 0) + freq
        self._total_freq_dict_trailing[len_ng] = \
            self._total_freq_dict_trailing.get(len_ng, 0) + freq
        # set self._freq_dict and self._total_freq_dict
        for i in range(len(seq) - len_ng + 1):
          ng = seq[i : i + len_ng]
          d = self._freq_dict.setdefault(len_ng, {})
          d[ng] = d.get(ng, 0) + freq
          self._total_freq_dict[len_ng] = \
              self._total_freq_dict.get(len_ng, 0) + freq

  @staticmethod
  def _get_ngs(lower_bound, upper_bound, freq_dict, total_freq):
    """Generates all n-grams for some length and bounds.

    Args:
      lower_bound: Percentile specifying the lower bound.
      upper_bound: Percentile specifying the upper bound.
      freq_dict: n-gram to frequency dictionary {n-gram:freq}.
      total_freq: Total frequency for all n-grams of the length.

    Returns:
      n-grams between specified bounds.
    """
    if not 0 <= lower_bound <= upper_bound <= 100:
      raise ValueError("Bounds must be 0 <= lower <= upper <= 100")
    # return nothing if total frequency is zero
    if total_freq == 0:
      return
    # sort by frequency, iterate and track the cumulative frequency
    cum_freq = 0.0
    passed_lower = False
    for (ng, freq) in sorted(freq_dict.items(), key=lambda x: x[1]):
      cum_freq += freq
      percentile = int(round(100 * cum_freq / total_freq))
      # yield if after lower and before upper, or if just passed both
      if lower_bound <= percentile and \
          (percentile <= upper_bound or not passed_lower):
        passed_lower = True
        yield ng

  def get_ngrams(self, length, lower_bound, upper_bound):
    """Gives all n-grams of some length between some bounds.

    Bounds must be lower and upper percentiles such that
    0 <= lower_bound <= upper_bound <= 100

    Args:
      length: Length of n-grams.
      lower_bound: Percentile specifying the lower bound.
      upper_bound: Percentile specifying the upper bound.

    Returns:
      n-grams of specified length and between specified bounds.
    """
    return self._get_ngs(lower_bound, upper_bound,
      self._freq_dict.get(length, {}), self._total_freq_dict.get(length, 0))

  def get_ngrams_leading(self, length, lower_bound, upper_bound):
    """Gives all leading n-grams of some length between some bounds."""
    return self._get_ngs(lower_bound, upper_bound,
      self._freq_dict_leading.get(length, {}), self._total_freq_dict_leading.get(length, 0))

  def get_ngrams_trailing(self, length, lower_bound, upper_bound):
    """Gives all trailing n-grams of some length between some bounds."""
    return self._get_ngs(lower_bound, upper_bound,
      self._freq_dict_trailing.get(length, {}), self._total_freq_dict_trailing.get(length, 0))

  def get_sequence_length_freq_dict(self):
    """Get the sequence length to frequency dictionary.

    Returns:
      A dictionary from sequence length to the total frequency of all
      sequences of that length.
    """
    return self._seq_len_dict

  def get_sequences(self):
    """Get the original sequences used when creating the SequenceAnalyzer.

    Returns:
      The input sequences (excluding the frequencies).
    """
    return self._seq_freq_dict.keys()

  def __imul__(self, other):
    """x.__imul__(y) <==> x*=y"""
    try:
      other = float(other)
    except:
      raise TypeError("unsupported operand type(s) for *: '%s' and '%s'" % (self, other))

    if other < 0:
      raise ValueError("can not multiply with negative numbers")

    # multiply other with value of dict of type {key1:{key2:value}}
    def mul_dict_dict(self_dict, other):
      for self_dict1 in self_dict.values():
        for (key2, value) in self_dict1.items():
          self_dict1[key2] = value * other

    # multiply other with value of dict of type {key:value}
    def mul_dict(self_dict, other):
      for (key, value) in self_dict.items():
        self_dict[key] = value * other

    for self_dict in \
        [self._freq_dict,
        self._freq_dict_leading,
        self._freq_dict_trailing]:
      mul_dict_dict(self_dict, other)

    for self_dict in \
        [self._total_freq_dict,
        self._total_freq_dict_leading,
        self._total_freq_dict_trailing,
        self._seq_len_dict,
        self._seq_freq_dict]:
      mul_dict(self_dict, other)

    return self

  def __mul__(self, other):
    """x.__mul__(n) <==> x*n

    Multiplies the frequencies of all sequences and n-grams with other.

    Args:
      other: Instance whose frequencies to multiply with. Must be positive.

    Returns:
      New instance resulting from the multiplication.

    Raises:
      TypeError: Multiplying with something that can not be casted to a float.
      ValueError: Multiplying with numbers lesser than zero.
    """
    result = copy.deepcopy(self)
    result *= other
    return result

  def __rmul__(self, other):
    """x.__rmul__(n) <==> n*x"""
    return self * other

  def __iadd__(self, other):
    """x.__iadd__(y) <==> x+=y"""
    if not isinstance(other, type(self)):
      raise TypeError("unsupported operand type(s) for +: '%s' and '%s'" % (self, other))

    # add values in dicts of type {key:value}
    def add_dict(self_dict, other_dict):
      for (other_key, other_value) in other_dict.items():
        self_dict[other_key] = self_dict.get(other_key, 0) + other_value

    # add values in dicts of type {key1:{key2:value}}
    def add_dict_dict(self_dict, other_dict):
      for (other_key1, other_dict1) in other_dict.items():
        self_dict1 = self_dict.setdefault(other_key1, {})
        for (other_key2, other_value) in other_dict1.items():
          self_dict1[other_key2] = self_dict1.get(other_key2, 0) + other_value

    for (self_dict, other_dict) in \
        [(self._total_freq_dict, other._total_freq_dict),
        (self._total_freq_dict_leading, other._total_freq_dict_leading),
        (self._total_freq_dict_trailing, other._total_freq_dict_trailing),
        (self._seq_len_dict, other._seq_len_dict),
        (self._seq_freq_dict, other._seq_freq_dict)]:
      add_dict(self_dict, other_dict)

    for (self_dict, other_dict) in \
        [(self._freq_dict, other._freq_dict),
        (self._freq_dict_leading, other._freq_dict_leading),
        (self._freq_dict_trailing, other._freq_dict_trailing)]:
      add_dict_dict(self_dict, other_dict)

    return self

  def __add__(self, other):
    """x.__add__(y) <==> x+y

    Adds the frequencies of all sequences and n-grams of two instances.

    Args:
      other: Instance whose frequencies to add.

    Returns:
      New instance resulting from the addition.

    Raises:
      TypeError: Adding with anything other than an instance of the same type.
    """
    result = copy.deepcopy(self)
    result += other
    return result

  @property
  def total_freq(self):
    """Sum of all added sequence frequencies.

    Setting total_freq to n is the equivalent of the operation
    self *= n / self.total_freq
    """
    return sum(self._seq_len_dict.values())

  @total_freq.setter
  def total_freq(self, value):
    if self.total_freq != 0:
      self *= float(value) / self.total_freq

def merge_normalized_sequence_analyzers(sequence_analyzers):
  """Merges SequenceAnalyzers and returns the result

  SequenceAnalyzers copied and normalized setting their individual total
  frequency to one. The sum of all normalized SequenceAnalyzers is then
  returned.

  Args:
    sequence_analyzers: List of SequenceAnalyzers to merge.

  Returns:
    The resulting normalized merge of the SequenceAnalyzers.
  """

  # copy input to avoid mutation
  sas_copy = [copy.deepcopy(sa) for sa in sequence_analyzers]

  # normalize sequences analyzers
  for sa in sas_copy:
    sa.total_freq = 1

  # add all sequences analyzers to the first
  for sa in sas_copy[1:]:
    sas_copy[0] += sa
  return sas_copy[0]
