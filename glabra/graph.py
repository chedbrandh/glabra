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

import itertools
import random
import sys

# for python 2 and python 3 compatibility
if sys.version_info < (3,):
    range = xrange

class GraphPathFinder(object):
  """Class for finding a path between two sets of vertices using an edge getter function.

  By prodiving a DirectedEdgeGetter instead of a whole (potentially very large)
  graph, memory can be saved while still being able to find paths between two
  sets of vertices.

  A GraphPathFinder is created on a per number-of-vertices basis. In order to
  find paths of different lengths, multiple GraphPathFinders must be created.
  Since the number of vertices are known, the distance from the root vertex is
  here referred to as a step. I.e. all start_vertices are at step 0 and all
  neighboring vertices (at distance 1) are at step 1.

  In the build phase the set of possible vertices at each step is populated.
  Note that a vertex with an edge to a vertex in a previous step might not
  have an edge to a vertex in the next step. This introduces the concept of
  "reachable" vertices. A reachable vertex at some step, is (indirectly)
  connected both to a start and an end vertex.

  The GraphPathFinder class does not have a method for providing an iterator of
  all paths in a random order. In order to provide such functionality all
  possible graphs must be kept in memory. This feature could however be created
  given the other methods provided here (presumably when the max number of
  possible graphs is known and not too great).
  """

  def __init__(self, start_vertices, end_vertices, num_vertices, directed_edge_getter):
    """Create a GraphPathFinder given start and end vertices.

    Args:
      start_vertices:
        All found paths start with a vertex in start_vertices.
      end_vertices:
        All found paths end with a vertex in end_vertices.
      num_vertices:
        All found paths consist of exactly num_vertices number of vertices.
      directed_edge_getter:
        DirectedEdgeGetter used to find vertices connected to start vertices
        via out edges, and to end vertices via in edges. It is also used to
        find those vertices neighbors and the neighbors' neighbors and so on.
        Note the importance of the required DirectedEdgeGetter property of an
        edge getting listed in both direction. E.g. for all vertices Y listed
        in get_end_vertices(X), X is listed in get_start_vertices(Y).
    """
    if len(start_vertices) < 1:
      raise ValueError("Set of start vertices must be non empty.")
    if len(end_vertices) < 1:
      raise ValueError("Set of end vertices must be non empty.")
    if num_vertices < 2:
      raise ValueError("Number of connected vertices must be greater than one.")

    self._start_vertices = start_vertices
    self._end_vertices = end_vertices
    self._num_vertices = num_vertices
    self._dedge = directed_edge_getter

    # list of reachable vertex sets
    # i.e. step 0 contains all start vertices and step -1 contains all end vertices
    # step 1 contains all vertices with an edge from both step 0 and 2
    self._step_sets = []

    # true if there is no path from start to end vertices
    self._is_disconnected = False

    # build step sets and determine if disconnected
    self._build_step_sets()

  def is_disconnected(self):
    """If no path exists between the start and end vertices, the graph is disconnected.

    Returns:
      True if the graph is disconnected and False otherwise.
    """
    return self._is_disconnected

  def get_random_path(self):
    """Get a random path from a start vertex to an end vertex.

    The random path is created by randomly selecting a vertex in the set of all
    connected vertices. One random neigbor is the selected in each direction.
    Then a neigbors neigbor is randomly selected, and so on until the set of
    start and the set of end vertices has been reached.

    Returns:
      A tuple of vertices of length num_vertices, where first vertex is in the
      set of start vertices and the last vertex is in the set of end
      vertices, and all vertices in between are connected according to the
      directed_edge_getter.
    """
    if self.is_disconnected():
      raise ValueError("Start and end vertices are disconnected.")

    # pick a random step set and a random vertex in that set to start with
    path = [None] * self._num_vertices
    start_step_index = random.randint(0, self._num_vertices - 1)
    start_step_set = self._step_sets[start_step_index]
    path[start_step_index] = random.choice(list(start_step_set))

    # fill earlier steps
    for i in reversed(range(1, start_step_index + 1)):
      vertices = self._dedge.get_start_vertices(path[i]).intersection(self._step_sets[i - 1])
      path[i - 1] = random.choice(list(vertices))

    # fill later steps
    for i in range(start_step_index, self._num_vertices - 1):
      vertices = self._dedge.get_end_vertices(path[i]).intersection(self._step_sets[i + 1])
      path[i + 1] = random.choice(list(vertices))

    return tuple(path)

  def get_all_paths(self):
    """Get an iterator of all possible paths from a start vertex to an end vertex.

    Returns:
      A an iterator of tuples of vertices of length num_vertices, where first
      vertex is in the set of start vertices and the last vertex is in the set
      of end vertices, and all vertices in between are connected according to
      the directed_edge_getter.
    """
    if self.is_disconnected():
      raise ValueError("Start and end vertices are disconnected.")
    return self._get_all_paths_generator()

  def _get_all_paths_generator(self):
    """Perform a depth first search and yield everytime a leaf vertex is visited."""
    # current path is stored in path
    path = [None] * self._num_vertices
    # currently visiting vertex step_index number of steps from root
    step_index = 0
    # all unvisited sibling vertices are stored at each step from root
    steps_vertices = [None] * self._num_vertices
    # start by populating step 0 with all reachable start vertices
    steps_vertices[step_index] = list(self._step_sets[0])
    # while there are still unvisited paths
    while step_index > -1:
      # get all remaining unvisited vertices at current step
      vertices = steps_vertices[step_index]
      if len(vertices) == 0:
        # if all vertices have been visited at the current step, then step back
        step_index -= 1
      else:
        # mark the visit of a vertex at the current step by removing it
        vertex = vertices.pop()
        # update the current path with the vertex
        path[step_index] = vertex
        # yield path if visiting a leaf vertex
        if step_index == self._num_vertices - 1:
          yield tuple(path)
        # else populate next steps_vertices with all reachable vertices connected to vertex
        else:
          steps_vertices[step_index + 1] = set(self._dedge.get_end_vertices(vertex)).\
              intersection(self._step_sets[step_index + 1])
          step_index += 1

  def _build_step_sets(self):
    """Build the list of reachable vertex sets.

    Step 0 starts out with the set of all start vertices, and step -1 starts
    out with the set of all end vertices. All the vertices of step 1 that are
    reachable from step 0 can be calculated with the directed_edge_getter. This
    does not mean that these vertices are reachable from the other direction
    however. Essentially what is done here is building one tree from each
    direction; one tree with a root at the start, and one at the end. When they
    meet somewhere in the middle, the vertices that don't have an edge in both
    directions are removed.

    If there is no path between the start and the end vertices, this is
    discovered during this process also.
    """
    # build step sets
    self._step_sets = [set() for i in range(self._num_vertices)]
    self._step_sets[0] = set(self._start_vertices).copy()
    self._step_sets[-1] = set(self._end_vertices).copy()

    # build intermediate steps
    earlier_index = 0
    later_index = self._num_vertices - 1
    while earlier_index < later_index - 1:

      earlier_set = self._step_sets[earlier_index]
      later_set = self._step_sets[later_index]

      # the smallest set takes the next step
      if len(earlier_set) < len(later_set):
        new_set = _expand(earlier_set, self._dedge.get_end_vertices)
        self._step_sets[earlier_index + 1] = new_set
        earlier_index += 1
      else:
        new_set = _expand(later_set, self._dedge.get_start_vertices)
        self._step_sets[later_index - 1] = new_set
        later_index -= 1

      # if no new vertices then the graph is disconnected
      if len(new_set) == 0:
        self._is_disconnected = True
        return

    # filter later intermediate steps
    for i in range(earlier_index, self._num_vertices - 1):
      expand_update(self._step_sets[i + 1], self._step_sets[i], self._dedge.get_end_vertices)
      if len(self._step_sets[i + 1]) == 0:
        self._is_disconnected = True
        return

    # filter early intermediate steps
    for i in reversed(range(1, later_index + 1)):
      expand_update(self._step_sets[i - 1], self._step_sets[i], self._dedge.get_start_vertices)
      if len(self._step_sets[i - 1]) == 0:
        self._is_disconnected = True
        return

def expand_update(the_set, other_set, expand_fn):
  """Updates a set with the intersection of the expanded other set.

  I.e.
  Updates the_set with the intersection of _expand(other_set, expand_fn).

  E.g.
  With expand_fn = lambda x: (10*x, 100*x), the_set = set([1, 20, 300]),
  and other_set = set([1, 2, 3])
  this function leaves the_set with set([20, 300])

  Args:
    the_set: A set of elements.
    other_set: Another set of elements.
    expand_fn: Function returning an interable given some element in other_set.

  Returns: The filtered the_set
  """
  the_set.intersection_update(_expand(other_set, expand_fn))
  return the_set

def _expand(the_set, expand_fn):
  """Returns a concatenation of the expanded sets.

  I.e.
  Returns a set of all elements returned by the expand_fn function for all
  elements in the_set.

  E.g.
  With expand_fn = lambda x: (10*x, 100*x) and the_set = set([1, 2, 3])
  this function returns set([10, 100, 20, 200, 30, 300])

  Args:
    the_set: A set of elements.
    expand_fn: Function returning an interable given some element in the_set.

  Returns: a concatenation of the expanded sets.
  """
  return set(itertools.chain(*[expand_fn(x) for x in the_set]))
