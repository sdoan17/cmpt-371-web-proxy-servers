import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8080
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

def build_200_response():
    file_path = PUBLIC_DIR / "test.html"
    body = file_path.read_bytes()

    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    return headers.encode() + body

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server running at http::??{HOST}:{PORT}/test.html")

    while True:
        connection_socket, client_address = server_socket.accept()

        with connection_socket:
            request = connection_socket.recv(4096).decode("iso-8859-1")
            print(f"\nRequest from {client_address}:")
            print(request)

            response = build_200_response()
            connection_socket.sendall(response)


