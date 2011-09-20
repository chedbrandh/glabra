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

def get_ngrams(sequence_analyzer, bounds):
  """Returns all n-grams within some bounds.

  Given a SequenceAnalyzer and some bounds, the n-grams that fulfill all
  the bounds' constraints are returned. To have all the constraints fulfilled
  here means that an n-gram must have bounds defined for its length (and
  be within those bounds), and if there are defined bounds for shorter
  n-grams, all sub-n-grams of that n-gram, of that shorter length, must be
  within those bounds also.

  E.g.
  SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])
  bounds = {3: (0, 100)}
  will return ["asd", "sdf", "qwe", "wer", "uip", "ipo"]

  E.g.
  SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])
  bounds = {2: (50, 100), 3: (0, 100)}
  (gives buckets ["po", "ui", "ip"] and ["uip", "ipo", "qwe", "wer", "asd", "sdf"])
  will return ["uip", "ipo"]

  Args:
    sequence_analyzer: SequenceAnalyzer to get n-grams from.
    bounds: Bounds that returned n-grams must be within.

  Returns:
    All n-grams that fulfill the bounds constraints.
  """
  get_ngs_fn = sequence_analyzer.get_ngrams
  get_filter_fn = _get_bucket_filter
  return _build_bucket(bounds, get_ngs_fn, get_filter_fn)

def get_ngrams_leading(sequence_analyzer, bounds_leading):
  """Returns all leading n-grams within some bounds.

  Like get_ngrams but only leading n-gram sub-n-grams must be within
  shorter bounds, if defined.

  E.g.
  SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])
  bounds = {3: (0, 100)}
  will return ["asd", "qwe", "uip"]

  E.g.
  SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])
  bounds = {2: (30, 100), 3: (0, 100)}
  (gives buckets ["ui", "qw"] and ["uip", "qwe", "asd"])
  will return ["uip", "qwe"]

  Args:
    sequence_analyzer: SequenceAnalyzer to get n-grams from.
    bounds: Bounds that returned n-grams must be within.

  Returns:
    All leading n-grams that fulfill all bounds constraints.
  """
  get_ngs_fn = sequence_analyzer.get_ngrams_leading
  get_filter_fn = _get_bucket_filter_leading
  return _build_bucket(bounds_leading, get_ngs_fn, get_filter_fn)

def get_ngrams_trailing(sequence_analyzer, bounds_trailing):
  """Returns all trailing n-grams within some bounds.

  Like get_ngrams but only trailing n-gram sub-n-grams must be within
  shorter bounds, if defined.

  E.g.
  SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])
  bounds = {3: (0, 100)}
  will return ["sdf", "wer", "ipo"]

  E.g.
  SequenceAnalyzer([("asdf", 1), ("qwer", 2), ("uipo", 3)])
  bounds = {2: (0, 80), 3: (0, 100)}
  (gives buckets ["er", "df"] and ["ipo", "wer", "sdf"])
  will return ["wer", "sdf"]

  Args:
    sequence_analyzer: SequenceAnalyzer to get n-grams from.
    bounds: Bounds that returned n-grams must be within.

  Returns:
    All trailing n-grams that fulfill all bounds constraints.
  """
  get_ngs_fn = sequence_analyzer.get_ngrams_trailing
  get_filter_fn = _get_bucket_filter_trailing
  return _build_bucket(bounds_trailing, get_ngs_fn, get_filter_fn)

def _build_bucket(bounds, get_ngs_fn, get_filter_fn):
  """Build bucket of n-grams that fulfill all bounds constraints.

  A list of n-gram buckets are first created using the provided bounds and a
  function for getting n-grams. The filter function is then used on the bucket
  with the longest n-grams to filter out the n-grams that don't "contain" the
  shorter n-grams.

  For example when getting leading n-grams for some given bounds, the
  SequenceAnalyzer.get_ngrams_leading function would be used for
  getting n-grams, and the _get_bucket_filter_leading function
  would be used for filtering.
  """
  ng_buckets = _get_ng_buckets(bounds, get_ngs_fn)
  _filter_ng_buckets(ng_buckets, get_filter_fn)
  return [] if (len(ng_buckets) == 0) else ng_buckets[-1]

def _get_ng_buckets(bounds, get_ngs_fn):
  """Given some bounds returns a list of lists of n-grams.

  n-grams are fetched using the get_ngs_fn function. n-grams of len x are
  fetched using the bounds at bounds[x], allowing only n-grams within the
  bounds. These lists of n-grams are added to the resulting list of lists of
  allowed n-grams. The returned list is ordered by length of n-grams, starting
  with the list with the shortest n-grams.

  Args:
    bounds: Tuples of lower and upper bound e.g. {3: (0, 100)}
    get_ngs_fn: Function returning n-grams between specified bounds.

  Returns:
    List of list of n-grams within bounds e.g. [["a", "b"], ["ab", "xy"]]
  """
  result = []
  for (len_ng, (lower_bound, upper_bound)) in sorted(bounds.items()):
    ng_bucket = get_ngs_fn(len_ng, lower_bound, upper_bound)
    result.append(list(ng_bucket))
  return result

def _filter_ng_buckets(ng_buckets, get_filter_fn):
  """Filters out n-grams that are not "contained" by shorter ones.

  Given a list of buckets of n-grams orderd by length of the n-grams,
  all n-grams in the last bucket (with the longest n-grams) that are not
  "contained" by n-grams in the previous buckets (with shorter n-grams) are
  filtered out.

  Starting with the two buckets with the shortest n-grams, a filter is
  obtained using the get_filter_fn and bucket #1. This filter is then applied
  to the n-grams in bucket #2 with longer n-grams. The same process is then
  repeated for bucket #2 and #3 and so on.

  E.g.
  get_filter_fn: _get_bucket_filter_leading
  ng_buckets: [["u", "a"], ["ui", "qw"], ["uip", "qwe", "asd"]]
  filters to: [["u", "a"], ["ui"], ["uip"]]
  step #1: ["u", "a"] filters ["ui", "qw"] to ["ui"]
  step #2: ["ui"] filters ["uip", "qwe", "asd"] to ["uip"]

  E.g.
  get_filter_fn: _get_bucket_filter_leading
  ng_buckets: [[], ["ui", "qw", "asd"], ["uip", "qwe", "asd"]]
  filters to: [[], [], []]

  Args:
    ng_buckets: List of buckets ordered by n-gram length.
    get_filter_fn: Function for getting filter, e.g. _get_bucket_filter.
  """
  for i in range(1, len(ng_buckets)):
    prev_ng_bucket = ng_buckets[i - 1]
    ng_bucket = ng_buckets[i]
    # if previous bucket is empty, current bucket automatically filters to
    # empty also. (or skip if current already is empty)
    if len(prev_ng_bucket) == 0 or len(ng_bucket) == 0:
      ng_buckets[i] = []
      continue
    # filter current bucket, only keep n-grams "contained" in previous
    len_prev_ng = len(prev_ng_bucket[0])
    len_ng = len(ng_bucket[0])
    assert len_prev_ng < len_ng
    ng_buckets[i] = list(filter(get_filter_fn(prev_ng_bucket, len_ng), ng_bucket))

def _get_bucket_filter(bucket, len_seq):
  """Filtering function determining if a sequence "contains" a bucket.

  All n-grams in the bucket must be of the same length. The sequence to be
  subject to the filtering function must be of length len_seq, and it must be
  longer than the n-grams in the bucket.

  A sequence is here defined as "containing" a bucket if all the n-grams of
  the sequence, of the same length as the n-grams in the bucket, are present
  in the bucket.

  E.g.
  bucket = ["as", "sd", "df", "qw", "er", "ui"]
  seqs = ["asdf", "qwer", "uiop"]
  seqs filters to: ["asdf"]

  Args:
    bucket: Bucket of n-grams used to filter sequences.
    len_seq: Length of sequences to be filtered.

  Returns:
    Filter function for sequence to be filtered "containing" bucket.
  """
  len_ng = len(bucket[0])
  assert len_ng < len_seq
  bucket_set = set(bucket)

  def filter_fn(seq):
    assert len(seq) == len_seq
    # check that all sequence n-grams are present in the bucket
    for i in range(len_seq - len_ng + 1):
      if not seq[i: i + len_ng] in bucket_set:
        return False
    return True

  return filter_fn

def _get_bucket_filter_leading(bucket, len_seq):
  """Filtering function for sequence "contains" a "leading bucket".

  All n-grams in the leading bucket must be of the same length. The length of
  the sequence to be subject to the filtering function must be of length
  len_seq, and it must be longer than the n-grams in the leading bucket.

  A sequence is here defined as "containing" a "leading bucket" if the leading
  n-gram of the sequence, of the same length as the n-grams in the bucket, is
  present in the bucket.

  E.g.
  bucket = ["as", "we", "op"]
  seqs = ["asdf", "qwer", "uiop"]
  seqs filters to: ["asdf"]

  Args:
    bucket: Bucket of n-grams used to filter sequences.
    len_seq: Length of sequences to be filtered.

  Returns: Filter function for sequence to be filtered "containing" bucket.
  """
  len_ng = len(bucket[0])
  assert len_ng < len_seq
  bucket_set = set(bucket)

  def filter_fn(seq):
    assert len(seq) == len_seq
    return seq[:len_ng] in bucket_set

  return filter_fn

def _get_bucket_filter_trailing(bucket, len_seq):
  """Filtering function for sequence "contains" a "trailing bucket".

  All n-grams in the leading bucket must be of the same length. The length of
  the sequence to be subject to the filtering function must be of length
  len_seq, and must be longer than the n-grams in the bucket.

  A sequence is here defined as "containing" a "trailing bucket" if the
  trailing n-gram of the sequence, of the same length as the n-grams in the
  bucket, is present in the bucket.

  E.g.
  bucket = ["as", "we", "op"]
  seqs = ["asdf", "qwer", "uiop"]
  seqs filters to: ["uiop"]

  Args:
    bucket: Bucket of n-grams used to filter sequences.
    len_seq: Length of sequences to be filtered.

  Returns: Filter function for sequence to be filtered "containing" bucket.
  """
  len_ng = len(bucket[0])
  assert len_ng < len_seq
  bucket_set = set(bucket)

  def filter_fn(seq):
    assert len(seq) == len_seq
    return seq[-len_ng:] in bucket_set

  return filter_fn
