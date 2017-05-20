hehreq
============

A small library with a couple of classes for asynchronous session-aware HTTP requests pushing with pipelining.
Maximum requests number during single Keep-Alive session is calculated using dichotomy.

Pydoc-generated documentation for the main class (hehreq.py) can be found in hehreq.html.

The FastGet and MassGet classes are hehreq wrappers for gevent-driven single and multiple hosts processing respectively.
They use Python logging interface to log stuff. They do not log 302 and 404 responses by default (see FastGet.report).

Prefix heh- in the name is from Avar "hehgo", which literally means "fast".

hehdirb
============

A wrapper which utilizes the capabilities of hehreq.

It also contains dirty script viewdirb.py for generating csv-reports of directory busting.
```
Usage: hehdirb.py [options]

Options:
  -h, --help            show this help message and exit
  -d DIC, --dictionary=DIC
                        input file with paths list
  -u URL, --url=URL     single URL to process
  -f URLS, --file=URLS  input file with URLs
  -t THREADS, --threads=THREADS
                        number of global workers
  -e EACH_THREADS, --each-threads=EACH_THREADS
                        number of workers for each host
  -k KEEPALIVE, --keep-alive=KEEPALIVE
                        Keep-Alive value (otherwise calculated)
  -r REPORT_DB, --report-db=REPORT_DB
                        JSON-encoded credentials (host, user, passwd, db)
```
Single host scanning with automatic session handling:
```
$ python hehdirb.py -u https://ya.ru/ -d tzar2.txt -t 200
WARNING:root:Calculated Keep-Alive: 100
WARNING:root:Path https://ya.ru:443/, response code 200, content-length 10429, content-type text/html; charset=UTF-8
. . .
TOTAL TIME 41.19 sec
TOTAL SPEED 227.73 rps
```
Single host scanning with predefined session duration:
```
$ python hehdirb.py -u https://ya.ru/ -d tzar2.txt -t 200 -k 100
WARNING:root:Calculated Keep-Alive for https://ya.ru/: 100
WARNING:root:Path https://ya.ru:443/, response code 200, content-length 10429, content-type text/html; charset=UTF-8
. . .
TOTAL TIME 8.71 sec
TOTAL SPEED 1076.46 rps
```
Multiple hosts scanning with predefined session duration:
```
$ cat urls
https://ya.ru/
https://mail.ru/
$ python hehdirb.py -f urls -d tzar2.txt -t 200 -k 100 -e 30
WARNING:root:Calculated Keep-Alive for https://ya.ru/: 100
WARNING:root:Calculated Keep-Alive for https://mail.ru/: 100
WARNING:root:Path https://ya.ru:443/, response code 200, content-length 10428, content-type text/html; charset=UTF-8
WARNING:root:Path https://mail.ru:443/, response code 200, content-length 253460, content-type text/html; charset=utf-8
. . .
TOTAL TIME 20.32 sec
TOTAL SPEED 461.61 rps
```
Scanning with MySQL logging:
```
$ python hehdirb.py -u https://ya.ru/ -d /home/beched/Desktop/TOOLS/web/tzar2.txt -t 200 -k 100 -r '{"host": "localhost", "user": "superdirb", "passwd": "***", "db": "superdirb"}'
WARNING:root:Calculated Keep-Alive for https://ya.ru/: 100
WARNING:root:Path https://ya.ru:443/, response code 200, content-length 10424, content-type text/html; charset=UTF-8
. . .
TOTAL TIME 14.70 sec
TOTAL SPEED 638.21 rps
```
Viewing the log:
```
mysql> select count(*) from scan_2017_05_20_224525;
+----------+
| count(*) |
+----------+
|     9380 |
+----------+
1 row in set (0,02 sec)

mysql> select count(*) from scan_2017_05_20_224525 where code=200;
+----------+
| count(*) |
+----------+
|       15 |
+----------+
1 row in set (0,01 sec)

mysql> select * from scan_2017_05_20_224525 limit 1,1;
+--------+-------+------+------+------+-------+--------------------------+
| scheme | host  | port | uri  | code | size  | type                     |
+--------+-------+------+------+------+-------+--------------------------+
| https  | ya.ru |  443 | 2008 |  404 | 12451 | text/html; charset=UTF-8 |
+--------+-------+------+------+------+-------+--------------------------+
1 row in set (0,00 sec)
```
Using the viewdirb.py to get csv log:
```
$ python viewdirb.py /tmp/out.csv
[*] Tables:
1) scan_2017_05_17_225245
2) scan_2017_05_20_224254
3) scan_2017_05_20_224313
4) scan_2017_05_20_224512
5) scan_2017_05_20_224525
> Choose index: 5
```