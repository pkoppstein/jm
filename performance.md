The following table shows execution times (u+s) and memory requirements (maximum resident set size)
when extracting the first item from a 120GB file containing a
flat top-level array of integers. 
The statistics were obtained on a 3GHz machine.

Note that [jstream](https://github.com/bcicen/jstream) does not always
preserve integer precision. The same is true of jq up to and including
jq 1.6.


Unless otherwise indicated, jaq version 0.10 (with hifijson) was used.

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
|134s  | 10.6MB| jaq 'first(.[])'
|130s  | 11.3MB| jaq '.[0]'
-------------------------------
|25m   | 10MB  | jaq .[]
|30m   | 13MB  | gojq --stream .
|53m   |  1.9MB| jq --stream .
|79m   |  7MB  | jstream -d 1
|90m   | 13MB  | jm
|2.4h  |123MB  | jm.py
|24h   |       | jq .[]


To determine the length of the array in the same 10GB file:
|u+s   | mrss  | command
|----- | ----- |  -------
|134s  | 9.9MB | gojq length ???? failed after consuming 100GB
| 27m  |13  MB | jm --count
| 54m  |18  MB | jm.py --count


/usr/bin/time -lp jq --stream . 1e9.json > /dev/null
user 3183.99
sys    40.35 
53m
             1 933 312  maximum resident set size
             1200128  peak memory footprint

previously
|2.5h  |       | jq --stream . 

