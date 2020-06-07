
Daniil Zakhlystov

**Anonymous proxy server**

HTTP Proxy server to block cookies! Cuts all Set-Cookie headers from the website responses...

Supports only HTTP1.0 and HTTP1.1

Usage: python main.py

By default, listening on localhost:8081

Default settings can be overriden by placing custom config.json in root folder


**Default options**
```javascript
{
  "port": 8081,
  "host": "",
  "threads_count": 2,
  "log_file": "log.txt",
  "max_req_time": 5,
  "queue_size": 5
}
```
