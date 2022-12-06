#!/usr/bin/env python3
# (C) Copyright Peter Koppstein (peak@princeton.edu)
# License: Apache License 2.0 (see website)
# Website: https://github.com/pkoppstein/jm
# Acknowledgements: the authors of ijson (https://pypi.org/project/ijson/)

# For help: $0 -h

# By default, input is assumed to be a top-level JSON array.
# In this case, the output will be a stream of the items in the array, one line per item.
# Read from stdin by default

# Using simplejson preserves integer literals and apparently decimal literals too.

import sys        # for argv, stderr
import argparse   # standard
from argparse import RawTextHelpFormatter

import ijson      # incremental parser
import simplejson # circumvent problem with decimals

bn='jm.py'
jmVersion='0.0.1 2022.12.05'

counter=0
counterPerFile=0

epilog=(f"""
The --limit and --count options are mutually exclusive,
as are the --s, --keys and --values options.

If no filename is specified, input will be taken from stdin.

One of the main uses of {bn} is to stream losslessly a JSON array or
JSON object that occurs at the top-level or within a very large JSON 
document.  (Losslessly here means without loss of precision of numbers,
not loss of information in objects with duplicate keys.)

In this document, streaming a JSON array is to be understood as
producing a stream of the top-level items in the array (one line per
item); similarly, streaming a JSON object means producing a stream of
the top-level keys or values, or of the key-value singleton objects if
the -s option is specified.  Streaming any other type of JSON entity
means printing it on a single line.

The --ipath option is used to specify the location in the input JSON
of the entity to be streamed.  The default value (namely 'item') is
appropriate if the input is a JSON array.  It is not an error for
there to be a mismatch between the path and the input JSON but if
there is a mismatch, no JSON output will be produced.

The ijson path for the top-level is ''. In general, an ijson path is a
string consisting of key names and/or the keyword 'item', joined by a
period. The keyword 'item' should be used where an array occurs but
may also be used if the key name is 'item'.  If a key includes a
period, the period need not be escaped.  These points are illustrated
in the last few examples below.

To stream a JSON object, the path specified by the --ipath option
should be the ijson path to that object, and one of the streaming
options for objects (i.e., one of -k, --keys, -s, --singleton, or
--values) should be specified.

""" + """

EXAMPLES:

The following examples assume this script is named jm.py, that it is
executable, and that the python3 executable can be found. The script
may also be invoked using a Python 3 interpreter.

jm.py <<< '[{"a": 0}, [{"b": 1}]'
{"a": 0}
{"b": 1}

jm.py -s <<< '[{"x": 0, "y": 1}]'
{"x": 0}
{"y": 1}

jm.py --keys <<< '[{"a": 0, "b": 1}]'
"a"
"b"

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
    metavar ='ipath',
    # required = True,
    dest ='ipath',
    action ='store',
    default='item',
    help ='the ijson path to the object or array to be streamed')

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

parser.add_argument('-v', dest ='verbose',
    action ='store_true',
    help ='verbose mode')

parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + jmVersion )

args = parser.parse_args()

if (args.singleton + args.values + args.keys) > 1:
    print(f"{bn}: at most one of the --singleton, --keys and --values options may be specified.", file=sys.stderr)
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

def maybePrint(msg):
    if not args.count:
        print(msg)

def process_entity(f):
    objects = ijson.items(f, args.ipath, multiple_values=True)
    for o in objects:
        maybePrint(simplejson.dumps(o))
        count()

def process_object(f):
    kvs = ijson.kvitems(f, args.ipath, multiple_values=True)
    for k, v in kvs:
        if not args.count:
          print('{' + simplejson.dumps(k) + ':', simplejson.dumps(v), end='')
          print('}')
        count()

def process_values(f):
    kvs = ijson.kvitems(f, args.ipath, multiple_values=True)
    for k, v in kvs:
        maybePrint(simplejson.dumps(v))
        count()
        
def process_keys(f):
    kvs = ijson.kvitems(f, args.ipath)
    for k, v in kvs:
        maybePrint(simplejson.dumps(k))
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
