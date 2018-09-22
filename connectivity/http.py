import time
import email


class HTTPRequestDecoder:

    @staticmethod
    def decode(data):
        request_text = data.decode()

        request_line, rest = request_text.split('\r\n', 1)
        headers_alone, body = rest.split('\r\n\r\n', 1)
        verb, path, version = request_line.split(' ')
        message = email.message_from_string(headers_alone)
        headers = dict(message.items())

        return verb, path, version, headers, body


class HTTPRequestEncoder:

    @staticmethod
    def encode(host, port, verb, path, body=None):
        h = verb + ' ' + path + ' ' + 'HTTP/1.1\r\nHost: ' + host + ':' + str(port) + '\r\n\r\n'
        if body:
            return (h + body).encode()
        return h.encode()


class HTTPResponseDecoder:

    @staticmethod
    def decode(data):
        splitted = data.decode().split('\r\n', 3)
        status = splitted[0].split(' ', 1)[1]
        date = splitted[1].split(' ', 1)[1]
        method = splitted[2].split(' ')[1]
        return status, date, method


class HTTPResponseEncoder:

    @staticmethod
    def header(code, verb):
        h = ''
        if code == 200:
            h = 'HTTP/1.1 200 OK\r\n'
        elif code == 201:
            h = 'HTTP/1.1 201 Created\r\n'
        elif code == 204:
            h = 'HTTP/1.1 204 No Content\r\n'
        elif code == 400:
            h = 'HTTP/1.1 400 Bad Request\r\n'
        elif code == 404:
            h = 'HTTP/1.1 404 Not Found\r\n'
        elif code == 409:
            h = 'HTTP/1.1 409 Conflict\r\n'
        elif code == 501:
            h = 'HTTP/1.1 501 Not Implemented\r\n'
        else:
            raise RuntimeError('Un recognized status code')  # TODO specific error

        # Optional headers
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\r\n'
        h += 'Request-Type: ' + verb + '\r\n'
        h += 'Server: Distributed-HTTP-Server\r\n'
        h += 'Content-Type: application/json\r\n'
        h += 'Connection: close\r\n\r\n'

        return h.encode()

    @staticmethod
    def encode(code, verb, content=None):
        header = HTTPResponseEncoder.header(code, verb)
        if content:
            return header + content.encode()
        return header
