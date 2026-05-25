import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS_LIST = [
    {
        "id": 1,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
    }
]


def validate_user_data(data, require_id=True):
    if not isinstance(data, dict):
        return False

    required_keys = ["username", "firstName", "lastName", "email", "password"]
    if require_id:
        required_keys.append("id")
        if "id" in data and not isinstance(data["id"], int):
            return False

    for key in required_keys:
        if key not in data or not isinstance(data[key], str) if key != "id" else False:
            return False
    return True


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, status_code=200, body=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body if body else {}).encode('utf-8'))

    def _pars_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return None
            return json.loads(self.rfile.read(content_length).decode('utf-8'))
        except Exception:
            return None

    def do_GET(self):
        global USERS_LIST

        if self.path == "/reset":
            USERS_LIST = [
                {
                    "id": 1,
                    "username": "theUser",
                    "firstName": "John",
                    "lastName": "James",
                    "email": "john@email.com",
                    "password": "12345",
                }
            ]
            self._set_response(200, USERS_LIST)
            return

        if self.path == "/users":
            self._set_response(200, USERS_LIST)
            return

        match = re.match(r"^/user/([^/]+)$", self.path)
        if match:
            username = match.group(1)
            user = next((u for u in USERS_LIST if u["username"] == username), None)
            if user:
                self._set_response(200, user)
            else:
                self._set_response(400, {"error": "User not found"})
            return

        self._set_response(404, {"error": "Not Found"})

    def do_POST(self):
        global USERS_LIST
        body = self._pars_body()

        if self.path == "/user":
            if body is None or not validate_user_data(body, require_id=True):
                self._set_response(400, {})
                return

            if any(u["id"] == body["id"] for u in USERS_LIST):
                self._set_response(400, {})
                return

            USERS_LIST.append(body)
            self._set_response(201, body)
            return

        if self.path == "/user/createWithList":
            if body is None or not isinstance(body, list):
                self._set_response(400, {})
                return

            for user_data in body:
                if not validate_user_data(user_data, require_id=True):
                    self._set_response(400, {})
                    return

            request_ids = [u["id"] for u in body]
            existing_ids = [u["id"] for u in USERS_LIST]

            if len(request_ids) != len(set(request_ids)) or any(rid in existing_ids for rid in request_ids):
                self._set_response(400, {})
                return

            USERS_LIST.extend(body)
            self._set_response(201, body)
            return

        self._set_response(404, {"error": "Not Found"})

    def do_PUT(self):
        global USERS_LIST

        match = re.match(r"^/user/(\d+)$", self.path)
        if match:
            user_id = int(match.group(1))
            body = self._pars_body()

            if body is None or not validate_user_data(body, require_id=False):
                self._set_response(400, {"error": "not valid request data"})
                return

            user = next((u for u in USERS_LIST if u["id"] == user_id), None)
            if not user:
                self._set_response(404, {"error": "User not found"})
                return

            user.update(body)
            self._set_response(200, user)
            return

        self._set_response(404, {"error": "Not Found"})

    def do_DELETE(self):
        global USERS_LIST

        match = re.match(r"^/user/(\d+)$", self.path)
        if match:
            user_id = int(match.group(1))

            user = next((u for u in USERS_LIST if u["id"] == user_id), None)
            if user:
                USERS_LIST.remove(user)
                self._set_response(200, {})
            else:
                self._set_response(404, {"error": "User not found"})
            return

        self._set_response(404, {"error": "Not Found"})


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host='localhost', port=8000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()