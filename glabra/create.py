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

import random

from glabra import graph
from glabra import dedge

class SequenceCreator(object):
  """Creates new sequences given sets of leading/middle/trailing n-grams.

  Sequences are created by taking one leading n-gram, one or more middle
  n-grams, one trailing n-gram, and concatenating them. The selected
  n-grams, in order, must "overlap as much as possible". The number of
  middle n-grams used depends on the length of the requested sequence to
  create. See DirectedEdgeGetter for the definition of "overlap" used here.

  When some sequence of n-grams (e.g leading-middle-middle-trailing) is
  found where all neigbors overlap each other according to the definition
  above, they are then concatenated with the overlap not duplicated.

  E.g.
  n-grams ["Icter", "teri", "eris", "rise"] concatenate to "Icterise".

  Using graph terminology, n-grams can be seen as vertices, and if two
  n-grams overlap they can be said to have a directed edge between them.
  The problem of finding a sequence of overlapping n-grams can therefore
  be translated to finding a path from some set of start vertices to some set
  of end vertices in this graph.
  """

  def __init__(self, sequence_length,
      ngrams_leading, ngrams_middle, ngrams_trailing):
    """n-grams are added and processed to prepare for sequence creation.

    Args:
      sequence_length: The length of the sequence to create.
      ngrams_leading: The leading n-grams.
      ngrams_middle: The middle n-grams.
      ngrams_trailing: The trailing n-grams.
    """

    # create edge getters from leading to middle and middle to trailing
    self._leading_to_middle_dedge = dedge.DirectedEdgeGetter(
        ngrams_leading, ngrams_middle)
    self._middle_to_trailing_dedge = dedge.DirectedEdgeGetter(
        ngrams_middle, ngrams_trailing)

    # get all middle vertices with edges to leading/trailing
    self._start_vertices = graph.expand_update(set(ngrams_middle),
        ngrams_leading, self._leading_to_middle_dedge.get_end_vertices)
    self._end_vertices = graph.expand_update(set(ngrams_middle),
        ngrams_trailing, self._middle_to_trailing_dedge.get_start_vertices)

    # return if there are no edges between middle and leading/trailing vertices
    if len(self._start_vertices) == 0 or len(self._end_vertices) == 0:
      self._is_disconnected = True
      return

    # get length of leading/middle/trailing n-grams
    len_leading = len(ngrams_leading[0])
    len_middle = len(ngrams_middle[0])
    len_trailing = len(ngrams_trailing[0])

    # calculate how many middle vertices are needed for the requested length
    num_middle_vertices = _get_num_middle_vertices(
        sequence_length, len_leading, len_middle, len_trailing)

    # if only one middle vertex is needed then no advanced path finding needs to happen
    if num_middle_vertices == 1:
      self._single_middle_vertex_init()
    else:
      self._multi_middle_vertex_init(ngrams_middle, num_middle_vertices)

  def _single_middle_vertex_init(self):
    """Setup sequence creation for the single middle vertex scenario.

    The pathfinding functions become only a matter of selecting a middle
    n-gram that overlaps with at least one leading and one trailing n-gram.
    """
    # only allowed middle vertices must have edge to both leading and trailing
    middle = self._start_vertices.intersection(self._end_vertices)
    if len(middle) == 0:
      self._is_disconnected = True
      return

    # a path in this scenario is simply one middle vertex
    self._is_disconnected = False
    self._get_random_path_fn = lambda: [random.choice(list(middle))]
    self._get_all_paths_fn = lambda: [[x] for x in middle] # [list(middle)]

  def _multi_middle_vertex_init(self, ngs_middle, num_middle_vertices):
    """Setup sequence creation for the multi middle vertex scenario.

    A graph pathfinder is created for the middle n-grams/vertices. Paths
    must start with a start vertex and end with an end vertex.
    """
    # create a graph path finder for the middle n-grams/vertices
    middle_to_middle_dedge = dedge.DirectedEdgeGetter(
        ngs_middle, ngs_middle)
    gpf = graph.GraphPathFinder(self._start_vertices, self._end_vertices,
        num_middle_vertices, middle_to_middle_dedge)

    # paths are gotten by calling methods in the graph path finder
    self._get_random_path_fn = gpf.get_random_path
    self._get_all_paths_fn = gpf.get_all_paths
    self._is_disconnected = gpf.is_disconnected()

  def is_disconnected(self):
    """Returns True if no sequence can be created."""
    return self._is_disconnected

  def get_random_sequence(self):
    """Returns a random sequence."""

    # error if disconnected
    if self.is_disconnected():
      raise ValueError("Provided n-grams are disconnected.")

    # get a random path through the middle vertices
    random_path = self._get_random_path_fn()

    # pick random leading/trailing vertices that have edges to the start/end vertices of the path
    ngram_leading = random.choice(list(
      self._leading_to_middle_dedge.get_start_vertices(random_path[0])))
    ngram_trailing = random.choice(list(
      self._middle_to_trailing_dedge.get_end_vertices(random_path[-1])))

    # return the concatenation of, one leading - many middle - one trailing, vertices/n-grams
    return _concat_ngram_list([ngram_leading] + list(random_path) + [ngram_trailing])

  def get_all_sequences(self):
    """Returns a generator of all possible sequences."""

    # error if disconnected
    if self.is_disconnected():
      raise ValueError("Provided n-grams are disconnected.")

    # for all paths of middle n-grams
    for path in self._get_all_paths_fn():
      # for all legal leading n-grams
      for ngram_leading in self._leading_to_middle_dedge.get_start_vertices(path[0]):
        # for all legal trailing n-grams
        for ngram_trailing in self._middle_to_trailing_dedge.get_end_vertices(path[-1]):
          # return the concatenation of leading, middle, and trailing vertices/n-grams
          yield _concat_ngram_list([ngram_leading] + list(path) + [ngram_trailing])

def _get_num_middle_vertices(len_seq, len_leading, len_middle, len_trailing):
  """Get the number of middle vertices required by the input.

  Exactly one leading and one trailing vertex will be used. At least one middle
  vertex will be used, but the longer the requested sequence the more middle
  vertices are required.

  Args:
    len_seq: The length of the requested sequence.
    len_leading: The length of the leading input n-grams.
    len_middle: The length of the middle input n-grams.
    len_trailing: The length of the trailing input n-grams.

  Returns:
    The number of middle vertices required.
  """
  # get the length of the resulting sequence if only one middle vertex is used
  len_single_middle_vertex = get_len_single_middle_vertex(len_leading, len_middle, len_trailing)
  # if requested sequence is longer, then more middle vertices are required
  return len_seq - len_single_middle_vertex + 1

def get_len_single_middle_vertex(len_leading, len_middle, len_trailing):
  """Get the length of the resulting sequence if only one middle vertex is used.

  Args:
    len_leading: The length of the leading input n-grams.
    len_middle: The length of the middle input n-grams.
    len_trailing: The length of the trailing input n-grams.

  Returns:
    The length of a one middle vertex sequence.
  """
  return (max(len_leading, len_middle) + 1) + \
      (max(len_trailing, len_middle) + 1) - len_middle

def _concat_ngram_list(ngram_list):
  """Concatenates a list of n-grams.

  Adjacent n-grams in the list are expected to be overlapping, and the
  overlap is not duplicated in the returned concatenation. The contents of the
  n-grams will not be checked however to verify the overlap.

  E.g.
  With ngram_list = ["abc", "bcde", "ef"]
  the concatenation becomes "abcdef"

  Args:
    ngram_list: The list of n-grams to concatenate.

  Returns:
    The concatenation of the n-grams provided.
  """
  result = ngram_list[0]
  for i in range(1, len(ngram_list)):
    prev_ngram = ngram_list[i - 1]
    ngram = ngram_list[i]
    len_overlap = min(len(prev_ngram), len(ngram)) - 1
    result += ngram[len_overlap:]
  return result
