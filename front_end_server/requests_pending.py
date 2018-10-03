from threading import Lock
import uuid


class RequestsPending:

    def __init__(self):
        self.mutex = Lock()
        self.clients = {}

    def new_request(self, client_conn):
        with self.mutex:
            req_id = uuid.uuid4().hex
            self.clients[req_id] = client_conn
            return req_id

    def get_client_from_request(self, req_id):
        with self.mutex:
            return self.clients[req_id]

    def request_completed(self, req_id):
        with self.mutex:
            del self.clients[req_id]
