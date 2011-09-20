from glabra import buckets
from glabra import analyze

class TestGetSeq(object):

  @classmethod
  def setup_class(cls):
    cls.sa = analyze.SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])

  def test_get_ngrams_simple(self):
    bounds = {3: (0, 100)}
    assert set(["asd", "sdf", "qwe", "wer", "uip", "ipo"]) == \
        set(buckets.get_ngrams(self.sa, bounds))

  def test_get_ngrams_rare_short_seqs(self):
    # gives buckets ["po", "ui", "ip"] and ["uip", "ipo", "qwe", "wer", "asd", "sdf"]
    bounds = {2: (60, 100), 3: (0, 100)}
    assert set(["uip", "ipo"]) == set(buckets.get_ngrams(self.sa, bounds))

  def test_get_ngrams_filter_empty(self):
    # gives buckets ["po", "ui", "ip"] and ["qwe", "wer", "asd", "sdf"]
    bounds = {2: (60, 100), 3: (0, 70)}
    assert set() == set(buckets.get_ngrams(self.sa, bounds))

  def test_get_ngrams_equal_bounds(self):
    bounds = {3: (70, 70)}
    assert buckets.get_ngrams(self.sa, bounds)[0] in ["ipo", "uip"]

class TestGetSeqLeading(object):

  @classmethod
  def setup_class(cls):
    cls.sa = analyze.SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])

  def test_get_ngrams_leading_simple(self):
    bounds = {3: (0, 100)}
    assert set(["asd", "qwe", "uip"]) == set(buckets.get_ngrams_leading(self.sa, bounds))

  def test_get_ngrams_leading_rare_short_seqs(self):
    # gives buckets ["ui", "qw"] and ["uip", "qwe", "asd"]
    bounds = {2: (30, 100), 3: (0, 100)}
    assert set(["uip", "qwe"]) == set(buckets.get_ngrams_leading(self.sa, bounds))

  def test_get_ngrams_leading_filter_empty(self):
    # gives buckets ["qw", "as"] and ["uip"]
    bounds = {2: (0, 70), 3: (60, 100)}
    assert set() == set(buckets.get_ngrams_leading(self.sa, bounds))

  def test_get_ngrams_leading_equal_bounds(self):
    # gives buckets ["ui"] and ["uip"]
    bounds = {2: (70, 70), 3: (60, 60)}
    assert set(["uip"]) == set(buckets.get_ngrams_leading(self.sa, bounds))

class TestGetSeqTrailing(object):

  @classmethod
  def setup_class(cls):
    cls.sa = analyze.SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])

  def test_get_ngrams_trailing_simple(self):
    bounds = {3: (0, 100)}
    assert set(["sdf", "wer", "ipo"]) == set(buckets.get_ngrams_trailing(self.sa, bounds))

  def test_get_ngrams_trailing_rare_short_seqs(self):
    # gives buckets ["er", "df"] and ["ipo", "wer", "sdf"]
    bounds = {2: (0, 80), 3: (0, 100)}
    assert set(["wer", "sdf"]) == set(buckets.get_ngrams_trailing(self.sa, bounds))

  def test_get_ngrams_trailing_filter_empty(self):
    # gives buckets ["er", "df"] and ["ipo"]
    bounds = {2: (0, 60), 3: (60, 100)}
    assert set() == set(buckets.get_ngrams_trailing(self.sa, bounds))

  def test_get_ngrams_trailing_equal_bounds(self):
    # gives buckets ["po"] and ["ipo"]
    bounds = {2: (70, 70), 3: (60, 60)}
    assert set(["ipo"]) == set(buckets.get_ngrams_trailing(self.sa, bounds))

class TestGetNGramBuckets(object):

  @classmethod
  def setup_class(cls):
    cls.sa = analyze.SequenceAnalyzer([("asd", 1), ("qwe", 2), ("as", 3), ("qw", 3)])

  def test_get_ng_buckets_full_range(self):
    bounds = {2: (0, 100)}
    result = buckets._get_ng_buckets(bounds, self.sa.get_ngrams)
    assert len(result) == 1
    assert len(result[0]) == 4
    assert "as" in result[0]
    assert "sd" in result[0]
    assert "qw" in result[0]
    assert "we" in result[0]

  def test_get_ng_buckets_low_range(self):
    bounds = {2: (0, 50)}
    result = buckets._get_ng_buckets(bounds, self.sa.get_ngrams)
    assert len(result) == 1
    assert len(result[0]) == 2
    assert "sd" in result[0]
    assert "we" in result[0]

  def test_get_ng_buckets_high_range(self):
    bounds = {2: (50, 100)}
    result = buckets._get_ng_buckets(bounds, self.sa.get_ngrams)
    assert len(result) == 1
    assert len(result[0]) == 2
    assert "as" in result[0]
    assert "qw" in result[0]

class TestFilterSSBuckets(object):

  def test_filter_ng_buckets_simple(self):
    get_filter_fn = buckets._get_bucket_filter_leading
    ng_buckets = [["u", "a"], ["ui", "qw"], ["uip", "qwe", "asd"]]
    buckets._filter_ng_buckets(ng_buckets, get_filter_fn)
    assert ng_buckets == [["u", "a"], ["ui"], ["uip"]]

  def test_filter_ng_buckets_empty(self):
    get_filter_fn = buckets._get_bucket_filter_leading
    ng_buckets = [[], ["ui", "qw", "as"], ["uip", "qwe", "asd"]]
    buckets._filter_ng_buckets(ng_buckets, get_filter_fn)
    assert ng_buckets == [[], [], []]

  def test_filter_ng_buckets_second_empty(self):
    get_filter_fn = buckets._get_bucket_filter_leading
    ng_buckets = [["a", "b"], [], ["apa", "bpa", "cpa"]]
    buckets._filter_ng_buckets(ng_buckets, get_filter_fn)
    assert ng_buckets == [["a", "b"], [], []]

class TestBucketFilter(object):

  def test_get_bucket_filter_shorter(self):
    bucket = ["as", "sd", "df", "qw", "er", "ui"]
    seqs = ["asdf", "qwer", "uiop"]
    filter_fn = buckets._get_bucket_filter(bucket, len(seqs[0]))
    assert list(filter(filter_fn, seqs)) == ["asdf"]

class TestBucketFilterLeading(object):

  def test_get_bucket_filter_leading_shorter(self):
    bucket = ["as", "we", "op"]
    seqs = ["asdf", "qwer", "uiop"]
    filter_fn = (buckets._get_bucket_filter_leading(bucket, len(seqs[0])))
    assert list(filter(filter_fn, seqs)) == ["asdf"]

class TestBucketFilterTrailing(object):

  def test_get_bucket_filter_trailing_shorter(self):
    bucket = ["as", "we", "op"]
    seqs = ["asdf", "qwer", "uiop"]
    filter_fn = (buckets._get_bucket_filter_trailing(bucket, len(seqs[0])))
    assert list(filter(filter_fn, seqs)) == ["uiop"]
