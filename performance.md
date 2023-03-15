The following table shows execution times (u+s) and memory requirements (maximum resident set size)
when extracting the first item from a 120GB file containing a
flat top-level array of integers. 
The statistics were obtained on a 3GHz machine.

Note that [jstream](https://github.com/bcicen/jstream) does not always
preserve integer precision. The same is true of jq up to and including
jq 1.6.


|u+s   | mrss  | command
|----- | ----- | -------
|0.00s |  3.4MB| gojq --stream -cn 'limit(1;inputs &#124; select(length==2) &#124; .[1])' < $FILE
|0.01s |  2MB  | jstream -d 1 < $FILE &#124; head -n 1
|0.04s |  1.8MB| jq --stream -cn 'limit(1;inputs &#124; select(length==2) &#124; .[1])' < $FILE
|0.07s | 13MB  | jm --limit 1 $FILE
|0.31s | 18MB  | jm.py --limit 1 $FILE

For a 10G file consisting of a single JSON array:

|u+s   | mrss  | command
|----- | ----- |  -------
|30m   | 13MB  | `gojq --stream`
|79m   | 7MB   | `jstream -d 1`
|90m   | 13MB  | `jm`
|2.4h  | 123MB | `jm.py`
|2.5h  |       | `jq --stream`
|24h   |       | `jq .[]`

`jaq` ran out of memory.

For the 10GB file:
* `jm` took 27 minutes and and 13MB mrss to report the length of the array.
* `jm.py` took 2.1 hours to report the length of the array.

