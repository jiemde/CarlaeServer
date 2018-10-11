Carlae is a simple HTTP Server for the [PyCom line of WiFi enabled devices](https://pycom.io/solutions/hardware/)

Example Main.py


```python
From HTTPServer import http_daemon

success = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close
Server: Carlae"""

def HelloWorld(*args):
  return success


path_to_handler = {
    "/": HelloWorld
}

http_daemon(ssid="Carlae",
            password="c4rl43",
            path_to_handler=path_to_handler)

```
