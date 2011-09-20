import pytest
import collections

from glabra import graph

class TestGraphPathFinder(object):

  @classmethod
  def setup_class(cls):
    # 11 - 21   31 - 41
    #    X
    # 12 - 22 - 32   42
    #    \    /    \
    # 13 - 23   33 - 43
    cls.dg1 = DirectedGraph()
    cls.dg1.add_edge(11, 21)
    cls.dg1.add_edge(11, 22)
    cls.dg1.add_edge(12, 21)
    cls.dg1.add_edge(12, 22)
    cls.dg1.add_edge(12, 23)
    cls.dg1.add_edge(13, 23)
    cls.dg1.add_edge(22, 32)
    cls.dg1.add_edge(23, 32)
    cls.dg1.add_edge(31, 41)
    cls.dg1.add_edge(32, 43)
    cls.dg1.add_edge(33, 43)

    start_vertices = [11, 12]
    end_vertices = [41, 42, 43]
    num_steps = 4
    cls.gpf1 = graph.GraphPathFinder(start_vertices, end_vertices, num_steps, cls.dg1)

    # graph with self loops
    cls.dg2 = DirectedGraph()
    cls.dg2.add_edge(1, 2)
    cls.dg2.add_edge(2, 2)
    cls.dg2.add_edge(2, 3)
    cls.dg2.add_edge(3, 3)
    cls.dg2.add_edge(3, 2)

    start_vertices = [1]
    end_vertices = [3]
    num_steps = 5
    cls.gpf2 = graph.GraphPathFinder(start_vertices, end_vertices, num_steps, cls.dg2)

  def test_constructor_general(self):
    assert self.gpf1.is_disconnected() is False
    assert self.gpf1._step_sets[0] == set([11, 12])
    assert self.gpf1._step_sets[1] == set([22, 23])
    assert self.gpf1._step_sets[2] == set([32])
    assert self.gpf1._step_sets[3] == set([43])

  def test_constructor_illegal(self):
    graph.GraphPathFinder([11], [21], 2, DirectedGraph())
    with pytest.raises(ValueError):
      graph.GraphPathFinder([], [21], 2, DirectedGraph())
    with pytest.raises(ValueError):
      graph.GraphPathFinder([11], [], 2, DirectedGraph())
    with pytest.raises(ValueError):
      graph.GraphPathFinder([11], [21], 1, DirectedGraph())

  def test_random_paths_general(self):
    result_set = set([(12, 22, 32, 43), (11, 22, 32, 43), (12, 23, 32, 43)])
    for _ in range(100):
      assert tuple(self.gpf1.get_random_path()) in result_set

  def test_all_paths_general(self):
    paths = set(self.gpf1.get_all_paths())
    assert 3 == len(paths)
    assert (12, 22, 32, 43) in paths
    assert (11, 22, 32, 43) in paths
    assert (12, 23, 32, 43) in paths

  def test_constructor_self_loops(self):
    assert self.gpf1.is_disconnected() is False
    assert self.gpf2._step_sets[0] == set([1])
    assert self.gpf2._step_sets[1] == set([2])
    assert self.gpf2._step_sets[2] == set([2, 3])
    assert self.gpf2._step_sets[3] == set([2, 3])
    assert self.gpf2._step_sets[4] == set([3])

  def test_random_paths_self_loops(self):
    result_set = set([(1, 2, 2, 2, 3), (1, 2, 2, 3, 3), (1, 2, 3, 2, 3), (1, 2, 3, 3, 3)])
    for _ in range(100):
      assert tuple(self.gpf2.get_random_path()) in result_set

  def test_all_paths_self_loops(self):
    paths = set(self.gpf2.get_all_paths())
    assert 4 == len(paths)
    assert (1, 2, 2, 2, 3) in paths
    assert (1, 2, 2, 3, 3) in paths
    assert (1, 2, 3, 2, 3) in paths
    assert (1, 2, 3, 3, 3) in paths

  def test_no_path(self):
    gpf = graph.GraphPathFinder([1], [2], 5, DirectedGraph())
    assert gpf.is_disconnected() is True
    with pytest.raises(ValueError):
      gpf.get_random_path()
    with pytest.raises(ValueError):
      gpf.get_all_paths()

  def test_three_step_path_connected(self):
    dg = DirectedGraph()
    dg.add_edge(11, 21)
    dg.add_edge(11, 22)
    dg.add_edge(22, 31)
    dg.add_edge(21, 32)

    start_vertices = [11]
    end_vertices = [32]
    num_steps = 3
    gpf = graph.GraphPathFinder(start_vertices, end_vertices, num_steps, dg)
    assert gpf.is_disconnected() is False
    assert list(gpf.get_all_paths()) == [(11, 21, 32)]
    assert gpf.get_random_path() == (11, 21, 32)

  def test_three_step_path_disconnected(self):
    gpf = graph.GraphPathFinder([11], [32], 3, DirectedGraph())
    assert gpf.is_disconnected() is True

  # testing with no internal vertices
  def test_two_step_path(self):
    dg = DirectedGraph()
    dg.add_edge(11, 21)
    dg.add_edge(11, 22)

    start_vertices = [11]
    end_vertices = [21]
    num_steps = 2
    gpf = graph.GraphPathFinder(start_vertices, end_vertices, num_steps, dg)
    assert gpf.is_disconnected() is False
    assert list(gpf.get_all_paths()) == [(11, 21)]
    assert gpf.get_random_path() == (11, 21)

  def test_two_step_path_disconnected(self):
    gpf = graph.GraphPathFinder([11], [32], 2, DirectedGraph())
    assert gpf.is_disconnected() is True

  def test_expand_update(self):
    expand_fn = lambda x: (10*x, 100*x)
    assert graph.expand_update(set([1, 20, 300]), set([1, 2, 3]), expand_fn) == set([20, 300])

  def test_expand(self):
    expand_fn = lambda x: (10*x, 100*x)
    assert graph._expand([1, 2, 3], expand_fn) == set([10, 100, 20, 200, 30, 300])

class DirectedGraph(object):
  """A DirectedEdgeGetter implementation only used for testing."""

  def __init__(self):
    self.start_to_end_dict = collections.defaultdict(set)
    self.end_to_start_dict = collections.defaultdict(set)

  def add_edge(self, start_vertex, end_vertex):
    self.start_to_end_dict[start_vertex].add(end_vertex)
    self.end_to_start_dict[end_vertex].add(start_vertex)

  def get_start_vertices(self, end_vertex):
    return self.end_to_start_dict[end_vertex]

  def get_end_vertices(self, start_vertex):
    return self.start_to_end_dict[start_vertex]
