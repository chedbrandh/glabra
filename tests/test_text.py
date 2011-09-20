import pytest
import mock

from glabra import analyze
from glabra import text

class TestTextGenerator(object):

  @classmethod
  def setup_class(cls):
    cls.sa = analyze.SequenceAnalyzer(
        [("ab", 1), ("bc", 1), ("cd", 1), ("de", 1), ("xxxx", 1)])
    cls.sa2 = analyze.SequenceAnalyzer(
        [("ab", 1), ("bc", 1), ("cd", 1), ("de", 1), ("yyyyy", 1)])
    cls.bounds = {2: (0, 100)}
    cls.tg = text.TextGenerator(cls.bounds, cls.sa)
    cls.tg2 = text.TextGenerator(cls.bounds, cls.sa2)

  def test_is_empty(self):
    bounds = {3: (0, 100)}
    text_generator = text.TextGenerator(bounds, self.sa)
    assert text_generator.is_empty()
    assert not self.tg.is_empty()

  def test_get_all_texts(self):
    assert set(self.tg.get_all_texts()) == set(["xxxx", "abcd", "bcde"])
    assert set(self.tg.get_all_texts(unique=True)) == set(["abcd", "bcde"])
    assert set(self.tg2.get_all_texts()) == set(["yyyyy", "abcde"])

  def test_get_random_texts(self):
    for text in self.tg.get_random_texts(100):
      assert text in set(["xxxx", "abcd", "bcde"])

    for text in self.tg.get_random_texts(100, unique=True):
      assert text in set(["abcd", "bcde"])

    for text in self.tg2.get_random_texts(100, unique=True):
      assert text == "abcde"

  def test_post_process(self):
    tg = text.TextGenerator(self.bounds, self.sa2, lambda x: x.capitalize() + "!")
    assert set(tg.get_all_texts(unique=True)) == set(["Abcde!"])

  def test_get_sequence_analyzer(self):
    file_content = "ab bc cd de xxxx"
    seq_delim = r"\s"

    with mock.patch("glabra.text.codecs.open",
        get_mock_file(file_content), create=True) as _:
      sa = text.get_sequence_analyzer("foo", seq_delim)
      assert set(sa.get_sequences()) == set(["ab", "bc", "cd", "de", "xxxx"])

  def test_get_sequence_analyzer_with_elem_delim(self):
    file_content = "a-5:b-34:xx-9-foo"
    seq_delim = ":"
    elem_delim = "-"

    with mock.patch("glabra.text.codecs.open",
        get_mock_file(file_content), create=True) as _:
      sa = text.get_sequence_analyzer(
          "foo", seq_delim, element_delimiter_pattern=elem_delim)
      assert set(sa.get_sequences()) == set([('a', '5'), ('b', '34'), ('xx', '9', 'foo')])

  def test_get_sequence_analyzer_with_frequencies(self):
    file_content = "a:4,b:6,c:77"
    seq_delim = ","
    freq_grouping = r"^(.+?):(\d*)$"

    with mock.patch("glabra.text.codecs.open",
        get_mock_file(file_content), create=True) as _:
      sa = text.get_sequence_analyzer(
          "foo", seq_delim, frequency_grouping_pattern=freq_grouping)
      assert sa._freq_dict[1]["a"] == 4
      assert sa._freq_dict[1]["b"] == 6
      assert sa._freq_dict[1]["c"] == 77

  def test_get_sequence_analyzer_empty(self):
    file_content = ""
    seq_delim = r"\s"

    with mock.patch("glabra.text.codecs.open",
        get_mock_file(file_content), create=True) as _:
      with pytest.raises(ValueError):
        text.get_sequence_analyzer("foo", seq_delim)

  def test_parse_bounds(self):
    bounds = text.parse_bounds(["3:0,100", "5:20,100"])
    assert bounds[3] == (0, 100)
    assert bounds[5] == (20, 100)

  def test_parse_bounds_negative_length(self):
    with pytest.raises(ValueError):
      text.parse_bounds(["-3:0,100"])

  def test_parse_bounds_out_of_bounds(self):
    with pytest.raises(ValueError):
      text.parse_bounds(["3:30,150"])
    with pytest.raises(ValueError):
      text.parse_bounds(["3:-30,50"])

  def test_parse_bounds_greater_lower_bound(self):
    with pytest.raises(ValueError):
      text.parse_bounds(["3:70,30"])

def get_mock_file(file_content):
  read_iter = iter([file_content, ""])
  def mock_read(*args, **kwargs):
    return next(read_iter)

  mock_file = mock.mock_open()
  mock_file().read = mock_read

  return mock_file
