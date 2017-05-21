import logging

from gevent import spawn
from gevent.queue import JoinableQueue
from datetime import datetime
from urlparse import urlparse

import MySQLdb

from .hehreq import HehReq

class FastGet:
    def __init__(self, url, dic, threads=100, report_db=False, keepalive=None, table_name=None):
        self.url = url
        parts = urlparse(url)
        self.scheme, self.host, self.port = parts.scheme, parts.hostname, parts.port
        if not self.port:
            self.port = 443 if self.scheme == 'https' else 80

        self.keepalive = keepalive
        try:
            instance = HehReq(self.host, int(self.port), self.scheme, self.keepalive)
        except Exception as e:
            logging.error('Init exception for %s: %s' % (self.url, e))
            return
        if not keepalive:
            self.keepalive = instance.detect_keepalive()
        if self.keepalive == 0:
            logging.error('Keep-Alive value for %s appears to be 0, check the connection' % url)
            return
        logging.warning('Calculated Keep-Alive for %s: %s' % (url, self.keepalive))

        self.report_db = report_db
        if report_db:
            self.table = table_name
            self.sql_conn(report_db)

        self.queue = JoinableQueue()
        [self.queue.put(dic[i:i + self.keepalive]) for i in xrange(0, len(dic), self.keepalive)]
        [spawn(self.worker) for _ in xrange(threads)]
        self.queue.join()

    def sql_conn(self, report_db):
        self.conn = MySQLdb.connect(report_db['host'], report_db['user'], report_db['passwd'], report_db['db'])
        self.cur = self.conn.cursor()
        if not self.table:
            self.table = 'scan_%s' % datetime.strftime(datetime.now(), '%Y_%m_%d_%H%M%S')
            self.cur.execute(
                'create table %s(scheme varchar(16), host varchar(128), port smallint, uri varchar(128),\
                code smallint, size int, type varchar(128))' % self.table)

    def report(self, result):
        if result[1] not in [302, 404]:
            logging.warning('Path %s://%s:%s/%s, response code %s, content-length %s, content-type %s' % (
                self.scheme, self.host, self.port, result[0], result[1], result[2], result[3]))
        if self.report_db:
            p = [self.scheme, self.host, self.port] + list(result)
            self.cur.execute('insert into %s values(%%s,%%s,%%s,%%s,%%s,%%s,%%s)' % self.table, p)

    def worker(self):
        try:
            instance = HehReq(self.host, int(self.port), self.scheme, self.keepalive)
        except Exception as e:
            logging.error('Worker init exception for %s: %s' % (self.url, e))
            return
        while not self.queue.empty():
            paths = self.queue.get()
            try:
                for x in instance.bulk_get(paths):
                    self.report(x)
            except Exception as e:
                logging.error('Worker loop exception for %s: %s' % (self.url, e))
            finally:
                if self.report_db:
                    self.conn.commit()
                self.queue.task_done()
