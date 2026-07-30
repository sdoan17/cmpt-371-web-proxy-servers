# CMPT 371 - Web and Web Proxy Servers

This repository contains the Option 1 mini project for CMPT 371. The project uses raw Python sockets to implement and test a minimal HTTP web server, a minimal web proxy, concurrent request handling, and frame-based head-of-line (HOL) blocking mitigation. Python HTTP modules and libraries are not used.

## Assignment Scope

- Specify the request conditions and test messages for `200 OK`, `304 Not Modified`, `403 Forbidden`, `404 Not Found`, and `505 HTTP Version Not Supported`.
- Build a minimal web server that serves the course-provided `test.html` file.
- Implement and test a minimal web proxy server.
- Make the web server respond to parallel requests in different threads and explain the performance impact.
- Use frames to mitigate HOL blocking and explain the result.

## Project Plan

1. Write the five status-code specifications and the HTTP request used to test each one.
2. Build and test the minimal raw-socket web server with the course-provided `test.html` file.
3. Specify, build, and test the minimal proxy server.
4. Add multithreaded request handling and document the parallel-request result.
5. Add frame-based response handling to mitigate HOL blocking and document the result.
6. Assemble the required Python files, modified HTML files if any, evidence, and PDF report for submission.

The detailed implementation-ready plan will be stored in `docs/plans/`.

## Repository Layout

```text
src/            Python server and proxy source files
public/         Course-provided test.html and other served files
tests/          Automated or manual test helpers and fixtures
docs/evidence/  Saved request/response output and screenshots for the report
docs/plans/     Project planning documents
```

