import socket


HOST = "127.0.0.1"
PORT = 9090


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))

    #Request one large and three small objs
    requests = (
        "GET /largeOTest.html HTTP/1.1\r\n"
        "Host: 127.0.0.1:9090\r\n"
        "\r\n"
        "GET /smallO1Test.html HTTP/1.1\r\n"
        "Host: 127.0.0.1:9090\r\n"
        "\r\n"
        "GET /smallO2Test.html HTTP/1.1\r\n"
        "Host: 127.0.0.1:9090\r\n"
        "\r\n"
        "GET /smallO3Test.html HTTP/1.1\r\n"
        "Host: 127.0.0.1:9090\r\n"
        "\r\n"
    )

    client_socket.sendall(requests.encode())
    client_socket.shutdown(socket.SHUT_WR)
    
    socket_file = client_socket.makefile("rb")

    responses = {1: b"", 2: b"", 3: b"", 4: b"",}

    finished = set()

    while len(finished) < 4:
        frame_head = socket_file.readline().decode().strip()

        parts = frame_head.split()

        objId = int(parts[1])
        final = int(parts[2])
        data_length = int(parts[3])

        frame_data = socket_file.read(data_length)
        responses[objId] += frame_data
        print(f"Received frame from Object {objId}, "f"frame is final flag = {final}")

        if final == 1:
            finished.add(objId)
            print(f"Object {objId} finished\n")


print("All objects were officially received")

for object_id in responses:
    response = responses[object_id]

    first_line = response.split(b"\r\n")[0].decode()

    print(f"Object {object_id}: "f"{first_line}, "f"{len(response)} bytes")