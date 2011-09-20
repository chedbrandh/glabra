from glabra import create

class TestSequenceCreator(object):

  @classmethod
  def setup_class(cls):
    length = 5
    leading = ["ax", "bx", "aa"]
    middle = ["xx", "xy", "yx", "yy", "zz", "xz"]
    trailing = ["x1", "x2", "11"]

    cls.sc1 = create.SequenceCreator(length, leading, middle, trailing)
    cls.sc2 = create.SequenceCreator(length, leading, ["xxx", "xyx"], trailing)

    cls.sc1_expected = set(["axxx1", "bxxx1", "axyx1", "bxyx1",
      "axxx2", "bxxx2", "axyx2", "bxyx2"])
    cls.sc2_expected = cls.sc1_expected

  def test_is_disconnected_false(self):
    assert not self.sc1.is_disconnected()

  def test_is_disconnected_true(self):
    assert create.SequenceCreator(5, ["aa"], ["xx"], ["11"]).is_disconnected()

  def test_get_random_sequence(self):
    # expected = set(["axxx1", "bxxx1", "axyx1", "bxyx1", "axxx2", "bxxx2", "axyx2", "bxyx2"])
    for _ in range(100):
      assert self.sc1.get_random_sequence() in self.sc1_expected

  def test_get_all_sequences(self):
    # expected = set(["axxx1", "bxxx1", "axyx1", "bxyx1", "axxx2", "bxxx2", "axyx2", "bxyx2"])
    actual = set(self.sc1.get_all_sequences())
    assert self.sc1_expected == actual

  def test_one_middle_node_random_sequence(self):
    # expected = set(["axxx1", "bxxx1", "axyx1", "bxyx1", "axxx2", "bxxx2", "axyx2", "bxyx2"])
    for _ in range(1):
      assert self.sc2.get_random_sequence() in self.sc2_expected

  def test_one_middle_node_all_sequences(self):
    # expected = set(["axxx1", "bxxx1", "axyx1", "bxyx1", "axxx2", "bxxx2", "axyx2", "bxyx2"])
    actual = set(self.sc2.get_all_sequences())
    assert self.sc2_expected == actual

  def test_varying_lengths(self):
    expected = set(["axxx1"])
    sc = create.SequenceCreator(5, ["axx"], ["xx"], ["x1"])
    assert set(sc.get_all_sequences()) == expected
    sc = create.SequenceCreator(5, ["ax"], ["xxx"], ["x1"])
    assert set(sc.get_all_sequences()) == expected
    sc = create.SequenceCreator(5, ["ax"], ["xx"], ["xx1"])
    assert set(sc.get_all_sequences()) == expected

    expected = set(["axxxx1"])
    sc = create.SequenceCreator(6, ["ax"], ["xxx"], ["xx1"])
    assert set(sc.get_all_sequences()) == expected
    sc = create.SequenceCreator(6, ["axx"], ["xx"], ["xx1"])
    assert set(sc.get_all_sequences()) == expected
    sc = create.SequenceCreator(6, ["axx"], ["xxx"], ["x1"])
    assert set(sc.get_all_sequences()) == expected

  def test_get_num_middle_vertices(self):
    assert create._get_num_middle_vertices(6, 2, 2, 2) == 3
    assert create._get_num_middle_vertices(4, 2, 2, 2) == 1
    assert create._get_num_middle_vertices(6, 2, 4, 2) == 1
    assert create._get_num_middle_vertices(6, 3, 2, 2) == 2

  def test_get_len_single_middle_vertex(self):
    assert create.get_len_single_middle_vertex(2, 2, 2) == 4
    assert create.get_len_single_middle_vertex(3, 2, 2) == 5
    assert create.get_len_single_middle_vertex(2, 2, 3) == 5
    assert create.get_len_single_middle_vertex(4, 10, 3) == 12

  def test_concat_ngram_list(self):
    assert create._concat_ngram_list(["ax", "xx", "x1"]) == "axx1"
    assert create._concat_ngram_list(["ax", "xzyzyzyx", "x1"]) == "axzyzyzyx1"
    assert create._concat_ngram_list(["axyxy", "xyx", "x1"]) == "axyxyx1"
    assert create._concat_ngram_list(["ax", "xx", "x123123"]) == "axx123123"
    assert create._concat_ngram_list(["ax", "xx123", "x123123"]) == "axx123123"
    assert create._concat_ngram_list(["abc", "bcde", "ef"]) == "abcdef"
