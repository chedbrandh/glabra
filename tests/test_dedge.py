import pytest

from glabra import dedge

class TestDirectedEdgeGetter(object):

  def test_success(self):
    start_ngs = ["sdfg", "sdru", "werz", "Werz", "1234"]
    end_ngs = ["fgx", "fgX", "sdr", "dru", "rup", "rzp"]
    edge = dedge.DirectedEdgeGetter(start_ngs, end_ngs)

    assert edge.get_end_vertices("sdfg") == set(["fgx", "fgX"])
    assert edge.get_end_vertices("sdru") == set(["rup"])
    assert edge.get_end_vertices("werz") == set(["rzp"])
    assert edge.get_end_vertices("1234") == set()

    assert edge.get_start_vertices("fgx") == set(["sdfg"])
    assert edge.get_start_vertices("fgX") == set(["sdfg"])
    assert edge.get_start_vertices("sdr") == set()
    assert edge.get_start_vertices("dru") == set()
    assert edge.get_start_vertices("rup") == set(["sdru"])
    assert edge.get_start_vertices("rzp") == set(["werz", "Werz"])

  def test_fail_empty_start_ngs(self):
    with pytest.raises(ValueError):
      dedge.DirectedEdgeGetter([], ["apa"])

  def test_fail_empty_end_ngs(self):
    with pytest.raises(ValueError):
      dedge.DirectedEdgeGetter(["apa"], [])

  def test_fail_illegal_ng_length_init(self):
    start_ngs = ["apa", "bpa", "oh long johnson"]
    end_ngs = ["foo", "bar"]

    with pytest.raises(ValueError):
      dedge.DirectedEdgeGetter(start_ngs, end_ngs)

  def test_fail_illegal_ng_length(self):
    start_ngs = ["apa", "bpa", "cpa"]
    end_ngs = ["foo", "bar"]
    edge = dedge.DirectedEdgeGetter(start_ngs, end_ngs)

    with pytest.raises(ValueError):
      edge.get_start_vertices("longcat")
