import socket
from datetime import datetime, timezone
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path
import threading

HOST = "127.0.0.1"
PORT = 8080
PUBLIC_DIR = Path(__file__).resolve().parent.parent

def build_response(status, body = b"", headers=None):
    response_headers = [
        f"HTTP/1.1 {status}",
        "Connection: close",
    ]

    if headers:
        response_headers.extend(headers)

    response_headers.append(f"Content-Length: {len(body)}")
    response = "\r\n".join(response_headers) + "\r\n\r\n"
    return response.encode() + body

def parse_request(request):
    lines = request.split("\r\n")
    method, path, version = lines[0].split()

    headers = {}

    for line in lines[1:]:
        if line == "":
            break

        if ":" in line:
            name, value = line.split(":", 1)
            headers[name.strip().lower()] = value.strip()
    
    return method, path, version, headers

def resolve_public_path(request_path):
    if ".." in request_path:
        return None
    
    return PUBLIC_DIR / request_path.lstrip("/")

def is_not_modified(file_path, if_modified_since):
    if not if_modified_since:
        return False
    
    try:
        client_date = parsedate_to_datetime(if_modified_since)
        file_modified = datetime.fromtimestamp(
            file_path.stat().st_mtime,
            timezone.utc,
        ).replace(microsecond=0)
        return file_modified <= client_date.astimezone(timezone.utc)
    except (TypeError, ValueError, IndexError):
        return False


def build_200_response(file_path):
    body = file_path.read_bytes()
    last_modified = formatdate(file_path.stat().st_mtime, usegmt = True)

    headers = (
        "Content-Type: text/html",
        f"Last-Modified: {last_modified}",
    )

    return build_response("200 OK", body, headers)

def build_304_response():
    return build_response("304 Not Modified")

def build_403_response():
    body = b"<html><body><h1>403 Forbidden</h1></body></html>"
    return build_response("403 Forbidden", body, ["Content-Type: text/html"])

def build_404_response():
    body = b"<html><body><h1>404 Not Found</h1></body></html>"
    return build_response("404 Not Found", body, ["Content-Type: text/html"])

def build_505_response():
    body = b"<html><body><h1>505 HTTP Version Not Supported</h1></body></html>"
    return build_response(
        "505 HTTP Version Not Supported",
        body,
        ["Content-Type: text/html"],
    )

def handle_client(connection_socket, client_address):
    with connection_socket:
        request = connection_socket.recv(4096).decode("iso-8859-1")

        print(f"\nRequest from {client_address}: {request}")

        method, path, version, headers = parse_request(request)

        if version != "HTTP/1.1":
            response = build_505_response()
        else:
            file_path = resolve_public_path(path)

            if file_path is None:
                response = build_403_response()
            elif not file_path.is_file():
                response = build_404_response()
            elif is_not_modified(file_path, headers.get("if-modified-since")):
                response = build_304_response()
            else: 
                response = build_200_response(file_path)
        
        connection_socket.sendall(response)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server running at http://{HOST}:{PORT}/test.html")

    while True:
        connection_socket, client_address = server_socket.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(connection_socket, client_address),
        )
        thread.start()

        

