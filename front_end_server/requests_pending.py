import uuid


class RequestsPending:
    clients = {}

    @staticmethod
    def new_request(client_conn):
        req_id = uuid.uuid4().hex
        RequestsPending.clients[req_id] = client_conn
        return req_id

    @staticmethod
    def get_client_from_request(req_id):
        return RequestsPending.clients[req_id]

    @staticmethod
    def request_completed(req_id):
        del RequestsPending.clients[req_id]
