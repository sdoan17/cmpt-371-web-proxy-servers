import socket

HOST = "127.0.0.1"
PORT = 8888

# Key: host, port, path
CACHE = {} 

def make_error(status):
    body = f"<html><body><h1>{status}</h1></body></html>".encode()

    return (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode() + body

def read_request(client_socket):
    request = b""

    while b"\r\n\r\n" not in request:
        data = client_socket.recv(4096)

        if not data:
            break

        request += data

    return request.decode("iso-8859-1")

def parse_url(url):
    if not url.startswith("http://"):
        raise ValueError

    url = url[len("http://"):]

    if "/" in url:
        host_port, path = url.split("/", 1)
        path = "/" + path
    else:
        host_port = url
        path = "/"

    if ":" in host_port:
        host, port = host_port.rsplit(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 80

    return host, port, path

def get_origin_response(host, port, path):
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode()

    response = b""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as origin_socket:
        origin_socket.connect((host, port))
        origin_socket.sendall(request)

        while True:
            data = origin_socket.recv(4096)

            if not data: 
                break
        
            response += data
    
    return response

def is_200_ok(response):
    first_line = response.split(b"\r\n", 1)[0]
    return b" 200" in first_line

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    proxy_socket.bind((HOST, PORT))
    proxy_socket.listen()

    print(f"Proxy running on {HOST}:{PORT}")

    while True:
        client_socket, client_address = proxy_socket.accept()

        with client_socket:
            try:
                request = read_request(client_socket)
                first_line = request.split("\r\n", 1)[0]
                method, url, version = first_line.split()

                if method != "GET":
                    response = make_error("501 Not Implemented")
                elif version != "HTTP/1.1":
                    response = make_error("505 HTTP Version not supported")
                else:
                    host, port, path = parse_url(url)
                    cache_key = (host, port, path)

                    if cache_key in CACHE:
                        print(f"CACHE HIT: {host}:{port}{path}")
                        response = CACHE[cache_key]
                    else:
                        print(f"CACHE MISS: {host}:{port}{path}")
                        response = get_origin_response(host, port, path)

                        if is_200_ok(response):
                            CACHE[cache_key] = response
                            print("Response saved in cache")
            except ValueError:
                response = make_error("400 Bad Request")
            except OSError:
                response = make_error("502 Bad Gateway")
            
            client_socket.sendall(response)