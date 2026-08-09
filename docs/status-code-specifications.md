# HTTP Status-Code Specifications

This document records the required request conditions and test messages for the minimal web server.

## 200 OK

- **Method:** `GET`
- **Request condition:** The requested path is an allowed file inside the public directory, and the file exists.
- **Request part that causes the response:** The request line names an existing file path, such as `/test.html`.
- **Response behavior:** Return `200 OK` and the requested file contents.

### Test Request

```http
GET /test.html HTTP/1.1
Host: localhost

```

### Expected Result

The server returns a response beginning with `HTTP/1.1 200 OK` and includes the contents of `public/test.html`.

## 304 Not Modified

- **Method:** `GET`
- **Request condition:** The requested file exists and has not been modified since the date supplied by the client.
- **Request part that causes the response:** The `If-Modified-Since` header contains the file's current `Last-Modified` value.
- **Response behavior:** Return `304 Not Modified` without sending the file body.

### Test Request

First request `/test.html` successfully and record its `Last-Modified` response header. Then send that exact value in this request:

```http
GET /test.html HTTP/1.1
Host: localhost
If-Modified-Since: <Last-Modified value returned by the server>

```

### Expected Result

The server returns a response beginning with `HTTP/1.1 304 Not Modified` and does not include the contents of `public/test.html`.

## 403 Forbidden

- **Method:** `GET`
- **Request condition:** The requested path would access a location outside the public directory.
- **Request part that causes the response:** The request target contains a parent-directory component such as `..`.
- **Response behavior:** Return `403 Forbidden` and do not read or return the requested file.

### Test Request

```http
GET /../private.txt HTTP/1.1
Host: localhost

```

### Expected Result

The server returns a response beginning with `HTTP/1.1 403 Forbidden`.

## 404 Not Found

- **Method:** `GET`
- **Request condition:** The requested path is allowed but no matching file exists in the public directory.
- **Request part that causes the response:** The request line names a missing file path.
- **Response behavior:** Return `404 Not Found`.

### Test Request

```http
GET /missing.html HTTP/1.1
Host: localhost

```

### Expected Result

The server returns a response beginning with `HTTP/1.1 404 Not Found`.

## 505 HTTP Version Not Supported

- **Method:** `GET`
- **Request condition:** The request uses an HTTP version that this minimal server does not support.
- **Request part that causes the response:** The protocol version token in the request line is not `HTTP/1.1`.
- **Response behavior:** Return `505 HTTP Version Not Supported`.

### Test Request

```http
GET /test.html HTTP/9.9
Host: localhost

```

### Expected Result

The server returns a response beginning with `HTTP/1.1 505 HTTP Version Not Supported`.

## References

- [RFC 7231: HTTP/1.1 Semantics and Content](https://datatracker.ietf.org/doc/html/rfc7231)
- [RFC 7232: HTTP/1.1 Conditional Requests](https://datatracker.ietf.org/doc/html/rfc7232)
