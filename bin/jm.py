#!/usr/bin/env python3
# (C) Copyright Peter Koppstein (peak@princeton.edu) 2022, 2023
# License: Apache License 2.0 (see website)
# Website: https://github.com/pkoppstein/jm
# Acknowledgements: the authors of ijson (https://pypi.org/project/ijson/)

# For help: $0 -h

# By default, input is assumed to be a top-level JSON array.
# In this case, the output will be a stream of the items in the array, one line per item.
# Read from stdin by default

# Using simplejson preserves integer literals and apparently decimal literals too.

# Notes on ijson:
#   multiple_values=True # allow a stream of JSON

# NEWS:
# 0.0.2 # --tag
# 0.0.3 # use multiple_values=True consistently
# 0.0.4 # use allow_comments=True if ijson.backend is "yajl2" or "yajl2_cffi") 

import sys        # for argv, stderr
import argparse   # standard
from argparse import RawTextHelpFormatter  # to print the epilog neatly

import ijson      # incremental parser
import simplejson # circumvent problem with decimals

bn='jm.py'
jmVersion='0.0.4 2023.01.09'

counter=0
counterPerFile=0

epilog=(f"""
The --limit and --count options are mutually exclusive,
as are the --tag, --s, --keys and --values options.

If no filename is specified, input will be taken from stdin.
Each input source can contain one or more top-level JSON entities.

One of the main uses of {bn} is to stream losslessly a JSON array or
JSON object that occurs at the top-level or within a very large JSON 
document.  (Losslessly here means without loss of precision of numbers,
not loss of information in objects with duplicate keys.)

In this documentation, streaming a JSON array is to be understood as
producing a stream of the top-level items in the array (one line per
item); similarly, streaming a JSON object means producing a stream of
the top-level keys or values, or of the key-value singleton objects if
the -s option is specified.  Streaming any other type of JSON entity
means printing it on a single line.

The default IPATH value is 'item', which is suitable for streaming a
top-level array.  See below for details about streaming JSON objects.

If --tag KEYNAME is specified, then instead of printing a JSON value, 
X, on a line, the values TAG and X are printed as tab-separated
values on a single line:

    TAG<tab>X

where TAG is the value associated with the key named KEYNAME if X is
an object with that key, or else empty.  That is, if X is not a JSON
object with the specified key, then no TAG is printed.

The --ipath option is used to specify the location in the input JSON
of the entity to be streamed.  The default value (namely 'item') is
appropriate if the input is a JSON array.  It is not an error for
there to be a mismatch between the path and the type of the
corresponding JSON entity but if there is a mismatch, no JSON output
will be produced.

The ijson path for the top-level is ''. In general, an ijson path is a
string consisting of key names and/or the keyword 'item', joined by a
period. The keyword 'item' should be used where an array occurs but
may also be used if the key name is 'item'.  If a key name includes a
period, the period need not be escaped.  These points are illustrated
in the last few examples below.

To stream a JSON object, the path specified by the --ipath option
should be the ijson path to that object, and one of the streaming
options for objects (i.e., one of -k, --keys, -s, --singleton, or
--values) should be specified; otherwise the object at the specified
location will be printed on a single line.

If the yajl library has been installed (e.g. via `brew install yajl`),
then /* C-style comments */ in the input will be ignored.
""" + """

EXAMPLES:

The following examples assume this script is named jm.py, that it is
executable, and that the python3 executable can be found. The script
may also be invoked using a Python 3 interpreter.

jm.py <<< '[{"a": 0}, [{"b": 1}]]'
{"a": 0}
[{"b": 1}]

jm.py -s <<< '[{"x": 0, "y": 1}]'
{"x": 0}
{"y": 1}

jm.py --keys <<< '[{"a": 0, "b": 1}]   [{"c": 2}]'
"a"
"b"
"c"

jm.py --tag x <<< '[{"x": "a\t"}, {"y": 0}]' | sed 's/\t/<tab>/'
"a\t"<tab>{"x": "a\t"}
<tab>{"y": 0}

jm.py --ipath '' <<< 100000000000000000000000000000000000000000000001
100000000000000000000000000000000000000000000001

jm.py -s --ipath '' <<< '{"x": 1.000000000000000000000001, "y": [1,2]}'
{"x": 1.000000000000000000000001}
{"y": [1, 2]}

jm.py --ipath 'inner.sanctum.item' <<< '{"inner": {"sanctum": [1,2]}}'
1
2

jm.py --ipath 'inner.item.sanctum.item' <<< '{"inner": [{"sanctum": [1,2] }, {"sanctum": [3,4] }] }'
1
2
3
4

jm.py --ipath 'item.item' <<< '{"item": [1,2]}'
1
2

jm.py --ipath 'x.y.item' <<< '{"x.y": [1,2]}'
1
2

PRE-REQUISITES:

python3
simplejson (https://pypi.org/project/simplejson)
ijson      (https://pypi.org/project/ijson)

""")

##########################################
parser = argparse.ArgumentParser(
    # prog="jm.py", # override $0
    description ='Stream a JSON array or object.',
    epilog = epilog,
    formatter_class=RawTextHelpFormatter # i.e. do not reformat the epilog
    )
 
parser.add_argument(
    dest ='filenames',
    metavar ='filename',
    nargs ='*')

parser.add_argument('-i', '--ipath',
    metavar ='IPATH',
    # required = True,
    dest ='ipath',
    action ='store',
    default='item',
    help ='the ijson path to the object or array to be streamed (defaut: item)')

parser.add_argument('-s', '--singleton', dest ='singleton',
    action ='store_true',    # on/off flag
    default=False,
    help ='stream JSON objects as single-key objects')

parser.add_argument('--values', dest ='values',
    action ='store_true',
    default=False,
    help ='stream JSON objects by printing the values of their keys')

parser.add_argument('-k', '--keys', dest ='keys',
    action ='store_true',
    default=False,
    help ='stream JSON objects by printing their keys')

parser.add_argument('--count', dest ='count',
    action ='store_true',
    help ='count the number of lines that would be printed')

parser.add_argument('--limit', dest ='limit',
    action ='store',
    type = int,
    help ='limit the number of JSON values (lines) printed')

parser.add_argument('--tag', dest ='tag',
    action ='store',
    metavar ='KEYNAME',
    help ='instead of emitting a line X of JSON, emit TAG<tab>X where TAG is determined by KEYNAME (see below)'
    )


parser.add_argument('-v', dest ='verbose',
    action ='store_true',
    help ='verbose mode')

parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + jmVersion )

args = parser.parse_args()

if (args.singleton + args.values + args.keys + (args.tag != None)) > 1:
    print(f"{bn}: at most one of the --tag, --singleton, --keys and --values options may be specified.", file=sys.stderr)
    exit(2)

if (args.limit and args.count):
    print(f"{bn}: at most one of the --limit and --count options may be specified.", file=sys.stderr)
    exit(2)
    
##########################################

def verbose(msg):
    if args.verbose:
        print(msg)
        
def count():
    global counter
    global counterPerFile
    counter += 1
    counterPerFile += 1
    # verbose(f"{bn}: counter={counter}")
    if args.limit and (counter >= args.limit):
        verbose(f"{bn}: limit {args.limit} reached")
        exit()

def process_entity(f):
    tag=args.tag
    objects = ijson.items(f, args.ipath, multiple_values=True, allow_comments=args.allow_comments)
    for o in objects:
        if not args.count:
            if tag:
                  if (type(o) is dict) and (tag in o):
                        print(simplejson.dumps(o[tag]), end='')
                  print("\t", end="")
            print(simplejson.dumps(o))
        count()

def process_entity_old(f):
    objects = ijson.items(f, args.ipath, multiple_values=True, allow_comments=args.allow_comments)
    for o in objects:
        if not args.count:
            print(simplejson.dumps(o))
        count()

def process_object(f):
    kvs = ijson.kvitems(f, args.ipath, multiple_values=True, allow_comments=args.allow_comments)
    for k, v in kvs:
        if not args.count:
          print('{' + simplejson.dumps(k) + ':', simplejson.dumps(v), end='')
          print('}')
        count()

def process_values(f):
    kvs = ijson.kvitems(f, args.ipath, multiple_values=True, allow_comments=args.allow_comments)
    for k, v in kvs:
        if not args.count:
        	print(simplejson.dumps(v))
        count()
        
def process_keys(f):
    kvs = ijson.kvitems(f, args.ipath, multiple_values=True, allow_comments=args.allow_comments)
    for k, v in kvs:
        if not args.count:
            print(simplejson.dumps(k))
        count()
        
def process(f):
    if args.singleton:
        process_object(f)
    elif args.keys:
        process_keys(f)
    elif args.values:
        process_values(f)
    else:
        process_entity(f)

verbose("ijson.backend is " + ijson.backend)
args.allow_comments=(ijson.backend == "yajl2_cffi" or ijson.backend == "yajl2" )

verbose(args)
# verbose(f"{bn}: ipath is {args.ipath}")

def bye():
    if args.count:
        print(counter)        

if len(args.filenames) == 0:
    f = open(0) # stdin
    process(f)
    bye()
    exit()

for file in args.filenames:
    f = open(file)
    counterPerFile=0
    process(f)
    f.close()
    if args.verbose and args.count:
        print(file, ": ", counterPerFile)

bye()
