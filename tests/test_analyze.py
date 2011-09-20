from glabra import analyze
from glabra.analyze import merge_normalized_sequence_analyzers as merge

class TestSequenceAnalyzer(object):

  @classmethod
  def setup_class(cls):
    cls.seqfreq1 = [("asdf", 1), ("qwer", 2), ("g", 3), ("ggg", 4), ("egg", 5)]
    cls.seqfreq2 = [("asd", 3), ("qwe", 2), ("zx", 1)]
    cls.seqfreq3 = [("asdf", 1), ("asdf", 2), ("asdf", 1)]
    cls.sa = analyze.SequenceAnalyzer(cls.seqfreq1)
    cls.sa2 = analyze.SequenceAnalyzer(cls.seqfreq2)
    cls.sa3 = analyze.SequenceAnalyzer(cls.seqfreq3)

  def test_get_ngrams(self):
    assert "g" in set(self.sa.get_ngrams(1, 0, 100))
    assert "g" in self.sa.get_ngrams(1, 99.9, 100.0)
    assert len(list(self.sa.get_ngrams(1, 0, 100))) == 9
    assert set(self.sa.get_ngrams(4, 0, 50)) == set(["asdf"])
    assert set(self.sa.get_ngrams(4, 50, 100)) == set(["qwer"])
    assert set((self.sa.get_ngrams(2, 50, 50))) == set(["eg"])
    assert next(self.sa2.get_ngrams(2, 0, 0)) == "zx"
    assert next(self.sa.get_ngrams(2, 100, 100)) == "gg"

  def test_get_ngrams_leading(self):
    assert "g" in self.sa.get_ngrams_leading(1, 0, 100)
    assert "g" in self.sa.get_ngrams_leading(1, 99.9, 100.0)
    assert len(list(self.sa.get_ngrams_leading(1, 0, 100))) == 4
    assert "g" in self.sa.get_ngrams_leading(1, 99, 100)
    assert len(list(self.sa.get_ngrams_leading(3, 0, 100))) == 4
    assert "asd" in self.sa.get_ngrams_leading(3, 0, 100.0/12.0)
    assert len(list(self.sa.get_ngrams_leading(3, 0, 100.0/12.0))) == 1
    assert set((self.sa.get_ngrams_leading(2, 20, 20))) == set(["qw"])
    assert next(self.sa.get_ngrams_leading(2, 0, 0)) == "as"
    assert next(self.sa.get_ngrams_leading(2, 100, 100)) == "eg"

  def test_get_ngrams_trailing(self):
    assert "g" in self.sa.get_ngrams_trailing(1, 0, 100)
    assert "g" in self.sa.get_ngrams_trailing(1, 99.9, 100.0)
    assert len(list(self.sa.get_ngrams_trailing(1, 0, 100))) == 3
    assert set(self.sa.get_ngrams_trailing(2, 0, 100.0/12.0)) == set(["df"])
    assert len(list(self.sa.get_ngrams_trailing(2, 0, 100))) == 3
    assert set((self.sa.get_ngrams_trailing(2, 20, 20))) == set(["er"])
    assert next(self.sa.get_ngrams_trailing(2, 0, 0)) == "df"
    assert next(self.sa.get_ngrams_trailing(2, 100, 100)) == "gg"

  def test_get_sequence_length_freq_dict(self):
    assert self.sa.get_sequence_length_freq_dict()[1] == 3
    assert self.sa.get_sequence_length_freq_dict()[3] == 9
    assert self.sa.get_sequence_length_freq_dict()[4] == 3
    assert 2 not in self.sa.get_sequence_length_freq_dict()

  def test_get_sequences(self):
    assert set(self.sa.get_sequences()) == set(["asdf", "qwer", "g", "ggg", "egg"])
    assert set(self.sa2.get_sequences()) == set(["asd", "qwe", "zx"])
    assert set(self.sa3.get_sequences()) == set(["asdf"])

  def test_imul(self):
    sa = analyze.SequenceAnalyzer(self.seqfreq1)
    (lb, ub) = (0.3, 0.7)
    ngrams_expected = list(sa.get_ngrams(2, lb, ub))
    sa *= 10
    # n-gram percentiles should stay the same
    assert list(sa.get_ngrams(2, lb, ub)) == ngrams_expected
    # sequence frequencies should be 10x
    assert sa._seq_freq_dict["asdf"] == 10
    assert sa._seq_freq_dict["g"] == 30
    assert sa._seq_freq_dict["egg"] == 50
    # n-gram frequencies should be 10x
    assert sa._freq_dict[2]["df"] == 10
    assert sa._freq_dict[2]["qw"] == 20
    assert sa._freq_dict[1]["g"] == 250

  def test_mul(self):
    sa = analyze.SequenceAnalyzer(self.seqfreq1)
    sa2 = sa * 10
    assert sa._seq_freq_dict["asdf"] == 1
    assert sa2._seq_freq_dict["asdf"] == 10

  def test_rmul(self):
    sa = analyze.SequenceAnalyzer(self.seqfreq1)
    sa2 = 10 * sa
    assert sa._seq_freq_dict["asdf"] == 1
    assert sa2._seq_freq_dict["asdf"] == 10

  def test_iadd(self):
    sa = analyze.SequenceAnalyzer(self.seqfreq1)
    sa2 = analyze.SequenceAnalyzer(self.seqfreq2)
    sa3 = analyze.SequenceAnalyzer(self.seqfreq3)
    sa += sa2
    # sequence frequences should change
    assert sa._seq_freq_dict["asdf"] == 1
    assert sa._seq_freq_dict["asd"] == 3
    # n-gram frequences should change
    assert sa._freq_dict[3]["asd"] == 4
    assert sa._freq_dict[2]["zx"] == 1
    assert sa._freq_dict[2]["we"] == 4
    # n-gram percentiles should change
    assert list(sa.get_ngrams(4, 100, 100)) == ["qwer"]
    sa += sa3
    assert list(sa.get_ngrams(4, 100, 100)) == ["asdf"]

  def test_add(self):
    sa = analyze.SequenceAnalyzer(self.seqfreq1)
    sa2 = analyze.SequenceAnalyzer(self.seqfreq2)
    sa3 = sa + sa2
    assert sa._freq_dict[3]["asd"] == 1
    assert sa3._freq_dict[3]["asd"] == 4

  def test_get_total_freq(self):
    assert self.sa.total_freq == 15

  def test_set_total_freq(self):
    sa = analyze.SequenceAnalyzer(self.seqfreq1)
    sa.total_freq = 150
    assert sa._seq_freq_dict["asdf"] == 10
    assert sa._seq_freq_dict["g"] == 30
    assert sa._seq_freq_dict["egg"] == 50
    assert sa._freq_dict[2]["df"] == 10
    assert sa._freq_dict[2]["qw"] == 20
    assert sa._freq_dict[1]["g"] == 250

  def test_freq_dict(self):
    assert self.sa._freq_dict[1]["a"] == 1
    assert self.sa._freq_dict[2]["sd"] == 1
    assert self.sa._freq_dict[1]["g"] == 25
    assert "x" not in self.sa._freq_dict[1]
    assert self.sa._freq_dict_leading[1]["a"] == 1
    assert self.sa._freq_dict_leading[2]["as"] == 1
    assert "x" not in self.sa._freq_dict_leading[1]
    assert "sd" not in self.sa._freq_dict_leading[2]
    assert self.sa._freq_dict_trailing[1]["f"] == 1
    assert self.sa._freq_dict_trailing[2]["df"] == 1
    assert "x" not in self.sa._freq_dict_trailing[1]
    assert "sd" not in self.sa._freq_dict_trailing[2]

  def test_total_freq_dict(self):
    assert self.sa._total_freq_dict[1] == 42
    assert self.sa._total_freq_dict[2] == 27
    assert self.sa._total_freq_dict[3] == 15
    assert self.sa._total_freq_dict[4] == 3
    assert 5 not in self.sa._total_freq_dict
    assert self.sa2._total_freq_dict[1] == 17
    assert self.sa2._total_freq_dict[2] == 11
    assert self.sa2._total_freq_dict[3] == 5
    assert 4 not in self.sa2._total_freq_dict

  def test_total_freq_dict_leading(self):
    assert self.sa._total_freq_dict_leading[1] == 15
    assert self.sa._total_freq_dict_leading[2] == 12
    assert self.sa._total_freq_dict_leading[3] == 12
    assert self.sa._total_freq_dict_leading[4] == 3
    assert 5 not in self.sa._total_freq_dict_leading
    assert self.sa2._total_freq_dict_leading[1] == 6
    assert self.sa2._total_freq_dict_leading[2] == 6
    assert self.sa2._total_freq_dict_leading[3] == 5
    assert 4 not in self.sa2._total_freq_dict_leading

  def test_total_freq_dict_trailing(self):
    assert self.sa._total_freq_dict_trailing[1] == 15
    assert self.sa._total_freq_dict_trailing[2] == 12
    assert self.sa._total_freq_dict_trailing[3] == 12
    assert self.sa._total_freq_dict_trailing[4] == 3
    assert 5 not in self.sa._total_freq_dict_trailing
    assert self.sa2._total_freq_dict_trailing[1] == 6
    assert self.sa2._total_freq_dict_trailing[2] == 6
    assert self.sa2._total_freq_dict_trailing[3] == 5
    assert 4 not in self.sa2._total_freq_dict_trailing

  def test_seq_len_dict(self):
    assert self.sa._seq_len_dict[1] == 3
    assert 2 not in self.sa._seq_len_dict
    assert self.sa._seq_len_dict[3] == 9
    assert self.sa._seq_len_dict[4] == 3
    assert 5 not in self.sa._seq_len_dict
    assert 1 not in self.sa2._seq_len_dict
    assert self.sa2._seq_len_dict[2] == 1
    assert self.sa2._seq_len_dict[3] == 5
    assert 4 not in self.sa2._seq_len_dict

class TestSequenceAnalyzerMerge(object):

  @classmethod
  def setup_class(cls):
    cls.seqfreq1 = [("foo", 1), ("bar", 1)]
    cls.seqfreq2 = [("foo", 999), ("baz", 999)]
    cls.sa1 = analyze.SequenceAnalyzer(cls.seqfreq1)
    cls.sa2 = analyze.SequenceAnalyzer(cls.seqfreq2)

  def test_merge_normalized_sequence_analyzers(self):
    sa_merge = merge([self.sa1, self.sa2])
    assert sa_merge._seq_freq_dict["foo"] == 1
    assert sa_merge._seq_freq_dict["bar"] == 0.5
    assert sa_merge._seq_freq_dict["baz"] == 0.5

  def test_merge_normalized_sequence_analyzers_no_mutation(self):
    merge([self.sa1, self.sa2])
    assert self.sa1._seq_freq_dict["foo"] == 1
    assert self.sa2._seq_freq_dict["foo"] == 999
