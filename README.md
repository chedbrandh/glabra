# Glabra

Glabra is a library for generating sequences using n-grams from other sequences
in some training data.

Glabra can be used to generate any kind of sequence including natural language
sequences. Sentence data can be used to generate sentences, and word data can
be used to generate words.

N-grams are extracted from the training data. N-gram length and n-gram lower
and upper frequency boundaries are then used to specify which of these n-grams
to use for sequence generation.

For example, if a length of 3, and frequency boundaries at the 50<sup>th</sup>
and the 100<sup>th</sup> percentile are specified, then all 3-grams in all
generated sequences will belong to the 50% most common 3-grams in the training
data.

The first and last (leading and trailing) n-grams are given special treatment.
The leading and trailing n-grams of the generated sequences are generated from
leading and trailing n-grams in the training data.

Since sequences are composed of not just regular n-grams but also leading and
trailing n-grams, generating a sequence becomes the problem of finding a path
of some length, from some set of start vertices, to some set of end vertices.
This problem is different from just running a Markov chain.

## Examples

The example scripts `generate_words.py` and `generate_sentences.py` demonstrate
how the library can be used to generate natural language. The limits of what
words and sentences that can be generated is only set by the number of data
sets that can be found (and the combination of them!).

### Generate US City Names
```sh
bash$ python examples/generate_text/generate_words.py --filename examples/generate_text/data/us_cities_most_populated.txt --get-random-words 5 --unique
Rocktonio
Planooga
Nashington
Portlano
Carlesto
```

### Generate Pokemon
```sh
bash$ python examples/generate_text/generate_words.py --filename examples/generate_text/data/pokemon.txt --get-random-words 5 --unique
Licketot
Ferroth
Aggronzor
Ledichu
Palpix
```

### Generate Bible Quotes
```sh
bash$ python examples/generate_text/generate_sentences.py --filename examples/generate_text/data/leviticus_niv.txt --bound 6:0,100 --word-delim "\s|\,|:|;" --sentence-delim "\.|\d" --get-random-sentences 5 --unique
Then Moses said to Aaron and his sons These are the regulations for a man with a discharge for anyone made unclean by an emission of semen.
You are to slaughter it at the north side of the altar before the Lord and Aaron’s sons the priests shall bring the blood and splash it against the sides of the altar.
Whether foreigner or native-born when they blaspheme the Name they are to be put to death their blood will be on their own head.
Whoever sits on anything that the man with a discharge touches without rinsing his hands with water must wash their clothes and they will be unclean till evening and then it will be clean.
The priest is to examine that person and if it is spreading in the skin the priest shall pronounce them unclean it is a defiling skin disease that has broken out where the boil was.
```

### Generate Swedish Idioms
```sh
bash$ python examples/generate_text/generate_sentences.py --filename examples/generate_text/data/swedish_idioms.txt --bound 3:0,100 --word-delim "\s" --sentence-delim "\n|\." --get-random-sentences 5 --unique
Som man sår får man ligga.
Gråt inte över ån efter vatten.
Pengar växer inte på en dag.
Bit inte den björn som sover.
Smaken är som krokodiler, stora i käften men saknar öron.
```
