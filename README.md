# jm and jm.py

`jm` and `jm.py` are scripts which make it easy to splat (that is, to
stream) JSON arrays or JSON objects losslessly, even if they occur in
very large JSON structures.  (Losslessly here refers primarily to
numeric precision, not the handling of duplicate keys within JSON
objects.)

Once installed, each script is typically trivial or very easy to use, e.g.
to splat the top-level array of a JSON document in a file named
input.json one could write:

    jm input.json

or

    jm.py input.json

For large inputs, `jm` is typically 3 or more times faster than `jm.py` and
consumes significantly less memory, but Pythonistas might find `jm.py`
of interest as it is easy to modify.

`jm` requires PHP and requires the installation of
[JSON Machine](https://github.com/halaxa/json-machine) package.

`jm.py` requires Python 3, and requires the installation of the
[ijson](https://pypi.org/project/ijson) package.

## Terminology
In this document, streaming a JSON array is to be understood as
producing a stream of the top-level items in the array (one line per
item), and similarly, streaming a JSON object means producing a stream
of the top-level values, or of the corresponding key-value singleton
objects if the -s option is specified.  Streaming other JSON values
simply means printing them.

## jm and jm.py similarities and differences
The two scripts are quite similar in terms of capabilties and
typical usage, but there are important differences, notably in the way
paths to subdocuments are specified: jm uses JSONPATH, whereas jm.py
has a less comprehensive notation.  As already illustrated, however,
typically no path need be specified at all.

### Numbers

`jm.py` preserves the precision of numbers, at least to the extent that
the ijson and simplejson packages allow.

The way in which `jm` prints JSON numbers depends on the `--recode`
and `--bigint_as_string` options, which are mutually exclusive:

  * --recode causes all JSON numbers to be presented as PHP numeric values
      with the potential loss of information this implies;
  * --bigint_as_string causes JSON "big integers" to be converted to
      strings to avoid loss of information, but other numbers will be
      converted to PHP numeric values;
  * if neither of these options is specified, the literal form of numbers is preserved.

### Synopsis of jm
```
Usage: jm [ OPTIONS ]  [ FILEPATH ... ]
or:    jm [-h | --help]
where FILEPATH defaults to stdin, and the other options are:
     -s | --keys | --tag KEYNAME
     --array
     --bigint_as_string | --recode
     --count | --limit=LIMIT
     --pointer=JSONPOINTER
     --version

JSONPOINTER defaults to ''.

The --tag option precludes the --array, --keys, and -s options.
```

For details, simply invoke the script with the --help option, or
review the documentation contained within the script itself.

### Synopsis of jm.py
```
usage: jm.py [-h] [-i IPATH] [-s] [--values] [-k] [--count] [--limit LIMIT] [--tag KEYNAME] [-v] [-V] [filename ...]

Stream a JSON array or object.

positional arguments:
  filename

options:
  -h, --help            show this help message and exit
  -i IPATH, --ipath IPATH
                        the ijson path to the object or array to be streamed
  -s, --singleton       stream JSON objects as single-key objects
  --values              stream JSON objects by printing the values of their keys
  -k, --keys            stream JSON objects by printing their keys
  --count               count the number of lines that would be printed
  --limit LIMIT         limit the number of JSON values (lines) printed
  --tag KEYNAME         instead of emitting a line X of JSON, emit TAG<tab>X where TAG is determined by KEYNAME (see below)
  -v                    verbose mode
  -V, --version         show program's version number and exit

The --limit and --count options are mutually exclusive,
as are the --tag, --s, --keys and --values options.

```
For details, simply invoke the script with the --help option, or
review the documentation contained within the script itself.

### Examples:
In these examples, $JM means that jm and jm.py  can be
used interchangeably.
```
(1) $JM <<< '[1,"2", {"a": 4}, [5.0000000000000000000000000006]]'
yields:
1
"2"
{"a":4}
[5.0000000000000000000000000006]
```
```
(2) $JM --tag a <<< '[{"a": 1}, {"a": [2]}, {"b": [3]}]' | sed 's/\t/<tab>/'
yields
1<tab>{"a": 1}
[2]<tab>{"a": [2]}
<tab>{"b": [3]}
```
```
(3) jm --keys <<< '{"a": 1, "b": [2]}'
is equivalent to
jm.py --keys --ipath '' <<< '{"a": 1, "b": [2]}'

Both yield:
"a"
"b"
```
```
(4) jm <<< '{"a": 1, "b": [2,3]}'
is equivalent to
jm.py --ipath '' --values <<< '{"a": 1, "b": [2,3]}'

Both yield:
1
[2,3]
```
```
(5) jm -s <<< '{"a": 1, "b": [2,3]}'
is equivalent to
jm.py --ipath '' -s <<< '{"a": 1, "b": [2,3]}'

Both yield:
{"a": 1}
{"b": [2,3]}
```
```
(6) jm --pointer "/results" <<< '{"results": {"a": 1, "b": [2,3]}}'
is equivalent to
jm.py --values --ipath "results" <<< '{"results": {"a": 1, "b": [2,3]}}'

Both yield the same stream as (4) above, namely:
1
[2, 3]
```
```
(7) jm --bigint_as_string <<< '[10000000000000000000002, 3.0000000000000000000004]'
yields
"10000000000000000000002"
3
```
```
(8) jm --array <<< '{"a": 1, "b": [2,3]}'
yields
[
1,
[2,3]
]
```
```
(9) jm --recode <(echo '[1.000000000000000001,20000000000000000003]')
yields
1
2.0e+19
```
```
(10) jm --pointer "/-" <<< '[1,[2,3]]'
yields
1
2
3
```
Note that in the last example, the JSON Pointer "/-" points in turn to
the items in the top-level array (i.e. 1 and then [2,3]), and that streaming 1 produces 1, and streaming [2,3]
produces 2 and then 3.


### Installation of jm

(1) Install "JSON Machine"

The simplest way to install "JSON Machine" is usually to run:
```
composer require halaxa/json-machine
```
in the user's home directory or in the same directory in which you intend to install the `jm` script.

To install `composer`, you could try `brew install composer` using
homebrew.  See "Additional Documentation" below for further details
and alternatives.

If you wish to clone or download the JSON Machine repository instead
of installing it using `composer`, then please note that `jm` will
assume it resides in the directory `~/github/json-machine/`.

(2) Download the file named `jm` from this repository.

If at all possible, ensure it is executable (e.g. `chmod +x jm`).
Otherwise, it can still be run as a PHP script, e.g. for help:
```
php jm --help
```

### Installation of jm.py

1) Ensure that both simplejson and ijson are installed, e.g.:
```
    pip install simplejson
    pip install ijson
```
2) Download the file named `jm.py` in the bin directory of this repository.

If at all possible, ensure it is executable (e.g. `chmod +x jm.py`).
Otherwise, it can still be run as a python3 script, e.g. for help:
```
python3 jm.py --help
```

### Performance Comparison

For a 10G file consisting of a single JSON array:

* `jstream -d 1` took 79 minutes with a small memory footprint (7MB maximum resident set size)
* `jm` took 90 minutes to run with minimal use of memory (to count took 27 minutes and 13MB)
* `jm.py` took 2.4 hours to run with a maximum resident set size of 123MB (to count took 2.1 hours)
* `jq` with the `--stream` option took over 2.5 hours to run
* `jq .[]` took 24 hours to finish
* `jaq` ran out of memory


Times shown are u+s times. [jstream](https://github.com/bcicen/jstream) does not always preserve integer precision.

### Additional Documentation

* "JSON Machine" e.g. https://github.com/halaxa/json-machine
* "JSON Pointer" e.g. https://www.rfc-editor.org/rfc/rfc6901#section-5
* composer       e.g. https://getcomposer.org/doc/00-intro.md
* homebrew       e.g. https://brew.sh

### Acknowledgements
Special thanks to https://github.com/halaxa, the creator of "JSON Machine".

Thanks also to the creators and maintainers of ijson.
