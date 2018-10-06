import time
import email
import logging


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


class HTTPResponseEncoder:
    code_as_string = {
        200: 'HTTP/1.1 200 OK\r\n',
        201: 'HTTP/1.1 201 Created\r\n',
        204: 'HTTP/1.1 204 No Content\r\n',
        400: 'HTTP/1.1 400 Bad Request\r\n',
        404: 'HTTP/1.1 404 Not Found\r\n',
        409: 'HTTP/1.1 409 Conflict\r\n',
        501: 'HTTP/1.1 501 Not Implemented\r\n'
    }

    @staticmethod
    def _header(code, content_len=None):
        if code in HTTPResponseEncoder.code_as_string:
            h = HTTPResponseEncoder.code_as_string[code]
        else:
            raise RuntimeError('Un recognized status code')

        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\r\n'
        if content_len is not None:
            h += 'Content-Length: ' + str(content_len) + '\r\n'
        h += 'Server: Distributed-HTTP-Server\r\n'
        h += 'Content-Type: application/json\r\n'
        h += 'Connection: close\r\n\r\n'

        return h.encode()

    @staticmethod
    def encode(code, content=None):
        if content:
            header = HTTPResponseEncoder._header(code, len(content))
            return header + content.encode()
        header = HTTPResponseEncoder._header(code)
        return header


class HTTPValidator:

    @staticmethod
    def is_HTTP_packet(data):
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger('HTTPValidator')
        logger.info("DATA: %r", data)
        ans = data.decode().split('\r\n\r\n')
        if len(ans) == 2 and ans[1] == "":
            ans = [ans[0]]
        head = ans[0].split('\r\n', 1)
        if len(head) < 2:
            return False
        message = email.message_from_string(head[1])
        headers = dict(message.items())
        return ('Content-Length' not in headers and len(ans) == 1) or \
               ('Content-Length' in headers and int(headers['Content-Length']) == len(ans[1]))
