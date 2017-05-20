import re
import socket
import ssl

class EnfOfStream(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class HehReq:
    def __init__(self, host, port=443, scheme='https', keepalive=100, timeout=5):
        '''
        Constructor, automatic connection
        :param host: hostname
        :param port: TCP port
        :param scheme: http or https
        :param keepalive: default maximum keepalive value
        :param timeout: socket timeout value
        '''
        self.host = host
        self.port = port
        self.scheme = scheme
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)
        self.keepalive = keepalive
        self.connect()

    def connect(self):
        '''
        Protocol-aware socket connection
        :return:
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.scheme == 'https':
            self.ssock = ssl.wrap_socket(sock)
        else:
            self.ssock = sock
        self.ssock.connect((self.host, self.port))
        self.ssock.settimeout(self.timeout)

    def reconnect(self):
        '''
        Close and reopen the socket
        :return:
        '''
        self.ssock.close()
        self.connect()

    def recv_until(self, find):
        '''
        Standard method for reading from socket until some string
        Raise an exception if nothing could be read
        :param find: string to reach
        :return:
        '''
        buf = ''
        while True:
            chunk = self.ssock.recv(1)
            if chunk == '':
                raise EnfOfStream
            buf += chunk
            if buf[-len(find):] == find:
                break
        return buf

    def encode(self, path):
        '''
        Partial urlencode
        :param path: URL
        :return:
        '''
        path = path.replace(' ', '+')
        path = path.replace('#', '%23')
        return path

    def get(self, path):
        '''
        Send HEAD request without reading respose
        :param path: URL to get
        :return:
        '''
        # TODO: Adding Connection:Keep-Alive may be needed in some cases...
        # TODO: Switching GET / HEAD ?
        packet = 'HEAD /%s HTTP/1.1\r\nHost:%s\r\n\r\n' % (path, self.host)
        self.ssock.send(packet)

    def detect_keepalive(self):
        '''
        Calculate maximum number of requests during single HTTP session
        :return: corresponding integer value
        '''
        l, r = 0, 1000
        while l + 1 < r:
            m = (l + r) / 2
            self.reconnect()
            try:
                for _ in self.bulk_get([''] * m, True):
                    pass
                l = m
            except:
                r = m
        self.keepalive = l
        return self.keepalive

    def bulk_get(self, paths, test=False):
        '''
        Get a bunch of URLs
        This is generator which yields tuples (URL, response code, Content-Length, Content-Type)
        :param paths: list of paths to get
        :param test: needed for keepalive calculation
        :return:
        '''
        for path in paths:
            self.get(path)
        for i in xrange(len(paths)):
            try:
                t = self.recv_until('\r\n\r\n')
                code = int(re.search(r'HTTP/1.. (\d+)', t).group(1))
                try:
                    length = int(re.search(r'Length\: (\d+)', t).group(1))
                except:
                    length = 0
                try:
                    contype = re.search(r'Type\: (.+)', t).group(1).strip()
                except:
                    contype = ''
                yield (paths[i], code, length, contype)
            except EnfOfStream:
                if test:
                    quit()
                self.reconnect()
                for x in self.bulk_get(paths[i:]):
                    yield x
                return

    def __del__(self):
        '''
        Destructor, close the socket
        :return:
        '''
        self.ssock.close()
