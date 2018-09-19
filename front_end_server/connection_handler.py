import uuid
import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPRequestDecoder
from http_server.sockets import ClientsSocket
from .bridge import Bridge


class RequestsPending:
    clients = {}

    @staticmethod
    def new_request(client_conn):
        req_id = uuid.uuid4().hex
        RequestsPending.clients[id] = client_conn
        return req_id

    @staticmethod
    def get_client_from_request(req_id):
        return RequestsPending.clients[req_id]

    @staticmethod
    def request_completed(req_id):
        del RequestsPending.clients[req_id]


class RequestReceiverThread:

    def __init__(self, bridge_host, bridge_port, servers):
        self.servers = servers
        self.bridge = Bridge(bridge_host, bridge_port, servers)

    def handle(self, conn, address):
        whoami = "FE-Worker-%r" % (address,)
        logger = logging.getLogger(whoami)

        try:
            conn = ClientsSocket(conn)
            logger.debug("Connected %r at %r", conn, address)

            data = conn.receive(1024)  # TODO receive up to request ending
            logger.debug("Received data %r", data)

            verb, path, version, headers, body = HTTPRequestDecoder.decode(data)
            logger.debug("Verb %r", verb)
            logger.debug("Path %r", path)
            logger.debug("Version %r", version)
            logger.debug("Headers %r", headers)
            logger.debug("Body %r", body)

            response = self.bridge.do_request(path, verb, body)

            conn.send(response)
            logger.debug("Sent data %r", response)

        except:
            logger.exception("Problem handling request")

        finally:
            logger.debug("Closing connection with client")
            conn.close()

    def close_bridge(self):
        self.bridge.shutdown()
