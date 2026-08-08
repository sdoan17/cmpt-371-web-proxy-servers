import socket
from datetime import datetime, timezone
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path
import threading

HOST = "127.0.0.1"
PORT = 9090
PUBLIC_DIR = Path(__file__).resolve().parent.parent

def build_response(status, body = b"", headers=None):
    response_headers = [
        f"HTTP/1.1 {status}",
        ##"Transfer-Encoding: chunked",
        "Connection: close",
    ]

    if headers:
        response_headers.extend(headers)

    response_headers.append(
        f"Content-Length: {len(body)}"
    )

    response = "\r\n".join(response_headers) + "\r\n\r\n"
    return response.encode(), body

def createFrames(objId, responseHead, body):
    response = responseHead + body
    frames = []

    for position in range(0, len(response), 1024):
        data = response[position:position + 1024]

        if position + 1024 >= len(response):
            final = 1
        else:
            final = 0

        frameHead = (
            f"FRAME {objId} {final} {len(data)}\r\n"
        ).encode()

        frame = frameHead + data
        frames.append(frame)

    return frames

def sendInFrames(connection_socket, objects):
    framesLeft = True

    while framesLeft == True:
        framesLeft = False

        for curObj in objects:
            frames = curObj["frames"]
            objId = curObj["objId"]

            if len(frames) > 0:
                framesLeft = True

                frame = frames.pop(0)

                connection_socket.sendall(frame)

                print(
                    f"Sent one frame from Object {objId}"
                )

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
        request_data = connection_socket.recv(4096).decode("iso-8859-1")

        print(f"\nRequest from {client_address}: {request_data}")

        request_lines = request_data.split("\r\n")

        objects = []
        objId = 1

        for request in request_lines:
            if request == "" or request == " ":
                continue

            try:
                method, path, version, headers = (parse_request(request))

                if version != "HTTP/1.1":
                    responseHead, body = build_505_response()
                else:
                    file_path = resolve_public_path(path)

                    if file_path is None:
                        responseHead, body = build_403_response()
                    elif not file_path.is_file():
                        responseHead, body = build_404_response()
                    elif is_not_modified(file_path, headers.get("if-modified-since")):
                        responseHead, body = build_304_response()
                    else: 
                        responseHead, body = build_200_response(file_path)
            except (ValueError, IndexError):
                responseHead, body = build_404_response()

            frames = createFrames(objId, responseHead, body,)

            currObj = {"objId": objId, "frames": frames,}

            objects.append(currObj)

            print(f"Object {objId} was divided into "f"{len(frames)} seperate frame(s)")

            objId = objId + 1

        #connection_socket.sendall(response)
        sendInFrames(connection_socket, objects)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server running on {HOST}:{PORT}")

    while True:
        connection_socket, client_address = server_socket.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(connection_socket, client_address),
        )
        thread.start()

        

