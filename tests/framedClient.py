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
        frameHead = socket_file.readline().decode().strip()
        parts = frameHead.split()

        objId = int(parts[1])
        final = int(parts[2])
        dataLen = int(parts[3])

        frameD = socket_file.read(dataLen)
        responses[objId] += frameD
        print(f"Received frame from Object {objId}, "f"frame is final flag = {final}")

        if final == 1:
            finished.add(objId)
            print(f"Object {objId} is finished\n")


print("All objects were officially received")

for objectId in responses:
    response = responses[objectId]

    firstL = response.split(b"\r\n")[0].decode()

    print(f"Object {objectId}: "f"{firstL}, "f"{len(response)} bytes")