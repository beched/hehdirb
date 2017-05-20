from gevent import monkey
monkey.patch_all()

import json
import sys
import time

from optparse import OptionParser

from hehreq import *


def encode(path):
    '''
    Partial urlencode
    :param path: URL
    :return:
    '''
    path = path.replace(' ', '+')
    path = path.replace('#', '%23')
    return path

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-d', '--dictionary', dest='dic',
                      help='input file with paths list')
    parser.add_option('-u', '--url', dest='url',
                      help='single URL to process')
    parser.add_option('-f', '--file', dest='urls',
                      help='input file with URLs')
    parser.add_option('-t', '--threads', dest='threads', default=100, type='int',
                      help='number of global workers')
    parser.add_option('-e', '--each-threads', dest='each_threads', default=10, type='int',
                      help='number of workers for each host')
    parser.add_option('-k', '--keep-alive', dest='keepalive', default=None, type='int',
                      help='Keep-Alive value (otherwise calculated)')
    parser.add_option('-r', '--report-db', dest='report_db', default=False,
                      help='JSON-encoded credentials (host, user, passwd, db)')

    (opts, _) = parser.parse_args()
    sys.setrecursionlimit(10000)
    st = time.time()

    if opts.report_db:
        opts.report_db = json.loads(opts.report_db)
    if not opts.dic:
        parser.print_help()
        quit()
    opts.dic = [encode(x.strip().lstrip('/')) for x in open(opts.dic, 'r').readlines()]
    if opts.url:
        num = 1
        FastGet(opts.url, opts.dic, opts.threads, opts.report_db, opts.keepalive)
    elif opts.urls:
        opts.urls = [x.strip() for x in open(opts.urls, 'r').readlines()]
        num = len(opts.urls)
        MassGet(opts.urls, opts.dic, opts.threads, opts.report_db, opts.keepalive, opts.each_threads)
    else:
        parser.print_help()
        quit()

    tt = time.time() - st
    print 'TOTAL TIME %.2f sec' % tt
    print 'TOTAL SPEED %.2f rps' % (num * len(opts.dic) / tt)
