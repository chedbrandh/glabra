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

ILLEGAL_LEN_MSG = "n-gram '{0}' is not of length {1}"

class DirectedEdgeGetter(object):
  """Finds edges between two sets of n-grams.

  Using graph terminology n-grams can be seen as vertices and if two
  n-grams "overlap as much as possible" they can be said to have a
  directed edge between them.

  Two n-grams "overlap as much as possible" if they both contain the same
  element sequence, only leaving one element on at least one of the
  n-grams.

  E.g.
  - "abc" and "bcd" overlap by this definition, and concatenate to "abcd".
  - "abcd" and "cdefg" do not overlap as much as possible however since the
    overlapping part "cd" leaves "ab" and "efg" (> one element) on each side.
  - "abcd" and "de" do overlap, with the overlap "d" leaving "abc" on the one
    side and "e" being the only element left on the other side.
  """

  def __init__(self, start_ngs, end_ngs):
    """Multimap dictionaries are created from the start/end n-grams.

    Args:
      start_ngs: The n-grams interpreted as vertices with directed edges
        coming out from them. All n-grams must be of the same length.
      end_ngs: The n-grams interpreted as vertices with directed edges
        going into them. All n-grams must be of the same length.
    """
    # validate the input
    if len(start_ngs) < 1 or len(end_ngs) < 1:
      raise ValueError("Must provide some start and end n-grams.")
    self._len_start = len(start_ngs[0])
    self._len_end = len(end_ngs[0])
    if self._len_start < 2 or self._len_end < 2:
      raise ValueError("n-grams must have a length greater than one.")
    self._len_overlap = min(self._len_start, self._len_end) - 1

    # create the multimap dictionaries
    self._start_overlap_dict = _get_start_overlap_dict(
      start_ngs, self._len_overlap, self._len_start)
    self._end_overlap_dict = _get_end_overlap_dict(
      end_ngs, self._len_overlap, self._len_end)

  def get_end_vertices(self, start_ng):
    """Get all end vertices/n-grams with an edge from some start n-gram.

    Args:
      start_ng: The n-gram to find connected end n-grams for.

    Returns:
      The set of end n-grams with an edge from start_ng. I.e. All
      n-grams that have an overlap with start_ng.
    """
    if len(start_ng) != self._len_start:
      raise ValueError(ILLEGAL_LEN_MSG.format(start_ng, self._len_start))
    return self._end_overlap_dict.get(start_ng[-self._len_overlap:], set())

  def get_start_vertices(self, end_ng):
    """Get all start vertices/n-grams with an edge to some end n-gram.

    Args:
      end_ng: The n-gram to find connected start n-grams for.

    Returns:
      The set of start n-grams with an edge to end_ng. I.e. All
      n-grams that have an overlap with end_ng.
    """
    if len(end_ng) != self._len_end:
      raise ValueError(ILLEGAL_LEN_MSG.format(end_ng, self._len_end))
    return self._start_overlap_dict.get(end_ng[:self._len_overlap], set())

def _get_end_overlap_dict(end_ngs, len_overlap, len_end):
  """Given end_ngs and len_overlap returns an overlap dictionary.

  The resulting overlap dictionary is intended to be used to find an overlap
  from one n-gram to other n-gram where there is an overlap of length
  len_overlap.

  The overlap dictionary will have keys of length len_overlap consisting of
  the len_overlap first elements in the end_ngs n-grams, and the value
  will be the n-gram itself.

  E.g.
  end_ngs = ["sdfg", "sdru", "werz", "1234"]
  len_overlap = 2
  returns {"sd": set(["sdfg", "sdru"]), "we": set(["werz"]), "12": set(["1234"])}

  end_ngs = ["sdf", "wdr", "wer", "123"]
  len_overlap = 1
  returns {"s": set(["sdf"]), "w": set(["wdr", "wer"], "1": set(["123"])}

  Args:
    end_ngs: The n-grams to be put in the overlap dictionary.
    len_overlap: The length of the n-gram overlap.
    len_end: The expected length of the n-grams in end_ngs. This is only
      used to validate the length of the contents of end_ngs.

  Returns:
    The overlap dictionary for the given n-grams.
  """
  result = {}
  for ng in end_ngs:
    assert len(ng) == len_end
    if len(ng) != len_end:
      raise ValueError(ILLEGAL_LEN_MSG.format(ng, len_end))
    result.setdefault(ng[:len_overlap], set()).add(ng)
  return result

def _get_start_overlap_dict(start_ngs, len_overlap, len_start):
  """Given start_ngs and len_overlap returns an overlap dictionary.

  This works the same way as _get_end_overlap_dict with the only difference
  being that the overlap is at the end of the n-grams in start_ngs.

  E.g.
  start_ngs = ["sdfg", "wefg", "werz", "1234"]
  len_overlap = 2
  returns {"fg": set(["sdfg", "werg"]), "rz": set(["werz"]), "34": set(["1234"])}

  start_ngs = ["sdf", "edr", "wer", "123"]
  len_overlap = 1
  returns {"f": set(["sdf"]), "r": set(["edr", "wer"], "3": set(["123"])}

  Args:
    start_ngs: The n-grams to be put in the overlap dictionary.
    len_overlap: The length of the n-gram overlap.
    len_start: The expected length of the n-grams in start_ngs. This is only
      used to validate the length of the contents of start_ngs.

  Returns:
    The overlap dictionary for the given n-grams.
  """
  result = {}
  for ng in start_ngs:
    if len(ng) != len_start:
      raise ValueError(ILLEGAL_LEN_MSG.format(ng, len_start))
    result.setdefault(ng[-len_overlap:], set()).add(ng)
  return result
