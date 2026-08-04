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
