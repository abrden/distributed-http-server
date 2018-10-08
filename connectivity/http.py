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
        200: '200 OK',
        201: '201 Created',
        204: '204 No Content',
        400: '400 Bad Request',
        404: '404 Not Found',
        409: '409 Conflict',
        501: '501 Not Implemented'
    }

    @staticmethod
    def _header(code, content_len=None):
        if code not in HTTPResponseEncoder.code_as_string:
            raise RuntimeError('Un recognized status code')

        date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        code_str = HTTPResponseEncoder.code_as_string[code]
        if content_len is None:
            h = "HTTP/1.1 {}\r\nDate: {}\r\nServer: Distributed-HTTP-Server\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n".format(code_str, date)
        else:
            h = "HTTP/1.1 {}\r\nDate: {}\r\nContent-Length: {}\r\nServer: Distributed-HTTP-Server\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n".format(code_str, date, content_len)

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
