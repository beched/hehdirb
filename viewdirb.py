# TODO: make this nice

import sys

from collections import Counter

import MySQLdb

output = open(sys.argv[1], 'wb')
conn = MySQLdb.connect(host="localhost",
                       user="superdirb",
                       passwd="***",
                       db="superdirb")
cur = conn.cursor()

cur.execute("select table_name from information_schema.tables where table_schema='superdirb'")
print '[*] Tables:'
tables = cur.fetchall()
for i in xrange(len(tables)):
    print '%s) %s' % (i + 1, tables[i][0])

table = tables[int(raw_input('> Choose index: ').strip()) - 1]

cur.execute('select * from %s where code!=404 and code!=302' % table)
# cur.execute('select * from %s where code=200' % table)
res = cur.fetchall()

out = {}
for x in res:
    url = '%s://%s:%s/' % (x[0], x[1], x[2])
    if url not in out:
        out.update({url: []})
    out[url].append(x[3:])

for h in out:
    t = Counter([x[2] for x in out[h]])
    size_404 = t.most_common(1)[0][0]
    for x in out[h]:
        if x[2] != size_404:
            output.write('%s%s\t%s\t%s\t%s\n' % (h, x[0], x[1], x[2], x[3]))
