"""Script contains simple socket api web server."""

import network
import gc
import re
import socket
import json


class Request:
    """Server HTTP request."""

    def __init__(self, raw_request):

        self.method, self.path, self.qparams, self.headers, self.body = self._parse(raw_request)

    def _parse(self, raw):
        """
        Parses raw client request.
        """

        lines = raw.split('\r\n')

        method = re.search('^([A-Z]+)', lines[0]).group(1)
        path = re.search('^[A-Z]+\\s+(/[-a-zA-Z0-9_.]*)', lines[0]).group(1)
        qparams = self._parse_qparams(lines, path)

        body_index = lines.index('')

        headers = self._parse_headers(lines[1:body_index-1])

        if lines[body_index + 1] != '':
            body = '\r\n'.join(lines[body_index + 1:-2]).strip()
        else:
            body = None
        
        return method, path, qparams, headers, body

    def _parse_headers(self, lines):
        """
        Parses request headers to dictionary.
        """

        headers = {}
        for line in lines:
            chunks = line.split(':', 1)
            if len(chunks) == 2:
                headers[chunks[0]] = chunks[1]

        return headers

    def _parse_qparams(self, lines, path):
        """
        Parses request query parameters to dictionary.
        """

        qparams = {}
        try:
            raw_qparams = lines[0].split(path)[1].split(' ')[0]
        except IndexError:
            qparams = {}
        else:
            for param in raw_qparams[1:].split('&'):
                chunks = param.split('=')
                if len(chunks) == 2:
                    qparams[chunks[0]] = chunks[1]

        return qparams


class Response:
    """Server HTTP response."""

    def __init__(self, data='', headers=None, code=200, status='OK'):
        
        self.data = data
        self.headers = headers if headers is not None else {}
        self.code = code
        self.status = status

    @property
    def raw(self):
        """
        Dumps response to text format.
        """

        if not isinstance(self.data, str):
            data = json.dumps(self.data)
        else:
            data = self.data

        headers = self.headers.copy()

        if 'Connection' not in headers:
            headers['Connection'] = 'close'
        if 'Content-Length' not in headers:
            headers['Content-Length'] = len(data)
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        response = 'HTTP/1.1 {} {}\r\n'.format(self.code, self.status)
        response += '\r\n'.join(['{}: {}'.format(key, value) for key, value in headers.items()])
        if data:
            response += '\r\n\r\n{}\r\n\r\n'.format(data)
        else:
            response += '\r\n\r\n\r\n'
        
        return response

    def __str__(self):
        """
        Dumps response to text format.
        """

        return self.raw
            

class Route:
    """Route artifacts container."""

    def __init__(self, path, method, handler):
        self.path = path
        self.method = method
        self.handler = handler


class MicroAPI:
    """Simple socket web API."""

    def __init__(self, wlan_id, wlan_pass):
        self.wlan_id = wlan_id
        self.wlan_pass = wlan_pass

        self._routes = []
        self._connection = None
        self._socket = None

    def route(self, path, method='GET'):
        """
        Decorator to register handler for given URL.
        """

        def wrapper(handler):
            self._routes.append(Route(path, method, handler))
            return handler

        return wrapper

    def connect(self):
        """
        Connects to local wifi network.
        """

        gc.collect()

        station = network.WLAN(network.STA_IF)
        station.active(True)
        station.connect(self.wlan_id, self.wlan_pass)

        while not station.isconnected():
            pass

        print('Connection successful.')
        print(station.ifconfig())

    def start(self):
        """
        Runs main server loop to handle requests.
        """

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('', 80))
        self._socket.listen(5)

        while True:

            if self._socket is None:
                break

            try:
                self._connection, address = self._socket.accept()

                print("[*] Connection from: {}".format(str(address)))

                raw_request = self._connection.recv(1024).decode("utf-8")

                if len(raw_request) == 0:
                    self._connection.close()
                    continue

                request = Request(raw_request)
                
                handler = self._find_handler(request)
                response = handler(request)

                print(response)

                if not isinstance(response, Response):
                    raise TypeError('Handler response must be type of "Response" object.')

                self._connection.sendall(str(response))
                
            except Exception as error:
                print(error)

            finally:
                self._connection.close()

    def _find_handler(self, request):
        """
        Returns handler associated with given request.
        Default not found handler is returned if handler does not exist.
        """

        handler = lambda req: Response({'message': 'Not Found'}, code=404, status='Not Found')

        for route in self._routes:
            if request.method == route.method and request.path == route.path:
                handler = route.handler
        
        return handler
