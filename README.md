# jm

`jm` is a PHP script for losslessly streaming JSON arrays or JSON objects,
even in very large JSON structures. It is based on, and requires the installation of,
[JSON Machine](https://github.com/halaxa/json-machine), but once installed
is typically trivial or very easy to use.

In this document, streaming a JSON array is to be understood as
producing a stream of the top-level items in the array (one line per
item), and similarly, streaming a JSON object means producing a stream
of the top-level values, or key-value singleton objects if the -s option is
specified.  Streaming other JSON values simply means printing them.
In particular, JSON numbers are handled literally.

"Losslessly" means without loss of numeric precision.

Once installed with its pre-requisites, the script is self-documenting
via the `--help` command-line option, but here are some examples.

## Examples:
```
(1) jm <<< '[1,"2", {"a": 4}, [5.0000000000000000000000000006]]'
yields:
1
"2"
{"a":4}
[5.0000000000000000000000000006]
```
```
(2) jm <<< '{"a": 1, "b": [2,3]}'
yields
1
[2,3]
```
```
(3) jm -s <<< '{"a": 1, "b": [2,3]}'
yields

{"a": 1}
{"b": [2,3]}
```
```
(4) jm --pointer "/results" <<< '{"results": {"a": 1, "b": [2,3]}}'
yields the same stream as (2) above.
```
```
(5) jm --pointer "/-" <<< '[1,[2,3]]'
yields
1
2
3
```
Note that in the last example, the JSON Pointer "/-" points in turn to
the items in the top-level array (i.e. 1 and then [2,3]), and that streaming 1 produces 1, and streaming [2,3]
produces 2 and then 3.


## Installation

(1) Install "JSON Machine"

The simplest way to install "JSON Machine" is to run:
```
composer require halaxa/json-machine
```
in the same directory in which you intend to install the `jm` script.

To install `composer`, you could try `brew install composer` using
homebrew.  See also "Additional Documentation" below. 

If you wish to clone or download the JSON Machine repository,
then `jm` will assume it resides in the directory `~/github/json-machine`.

(2) Download the file named `jm` from this repository.

If at all possible, ensure it is executable (e.g. `chmod +x jm`).
Otherwise, it can still be run as a PHP script, e.g. for help:
```
php jm --help
```
## Performance Comparison

For a 10G file consisting of a single JSON array:

* `vm` took 1.5 hours to run with minimal use of memory
* `jq` with the `--stream` option took over 2.5 hours to produce the same results
* `jq .[]' took 24 hours to finish
* `jaq` ran out of memory

## Additional Documentation

* "JSON Machine" e.g. https://github.com/halaxa/json-machine
* "JSON Pointer" e.g. https://www.rfc-editor.org/rfc/rfc6901#section-5
* composer       e.g. https://getcomposer.org/doc/00-intro.md
* homebrew       e.g. https://brew.sh

## Acknowledgements
Special thanks to https://github.com/halaxa, the creator of "JSON Machine".


