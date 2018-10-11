import socket
from network import WLAN


not_configured_response = """HTTP/1.1 404 Not Found
Content-Type: text/html
Connection: close
Server: OpenScale IoT

Endpoint not found"""


MAX_HTTP_MESSAGE_LENGTH = 2048


def http_daemon(ssid="OpenScale",
                password="OpenScale1!",
                path_to_handler={}):
    host_ip = "192.168.4.1"
    print("Creating Access Point {} with password {}".format(ssid, password))
    print("User will need to connect to the webpage at {}".format(host_ip))

    wlan = WLAN()
    wlan.deinit()
    wlan.ifconfig(config=(host_ip, '255.255.255.0', '0.0.0.0', '8.8.8.8'))
    wlan.init(mode=WLAN.AP, ssid=ssid, auth=(WLAN.WPA2, password), channel=5, antenna=WLAN.INT_ANT)

    # The address of the board at port 80
    address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(address)
    s.listen(5)

    print('listening on ', address)

    while True:
        connection_socket, address = s.accept()
        connection_socket.setblocking(False)
        print('New connection from', address)

        msg = connection_socket.recv(MAX_HTTP_MESSAGE_LENGTH).decode()
        msg = msg.replace("\r\n", "\n")

        blank_line_split = msg.split('\n\n')
        if len(blank_line_split) != 2:
            raise Exception("Malformated HTTP request.")

        preamble = blank_line_split[0].split("\n")
        request = preamble[0]
        request_keys = ["method", "path", "version"]
        request_key_value = zip(request_keys, request.split(" "))
        request = {key: value for key, value in request_key_value}

        headers = preamble[1:]
        headers = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in headers}

        for key, value in headers.items():
            request[key] = value

        print("Received Request:\n{}".format(request))

        request['body'] = blank_line_split[1]
        if 'Content-Length' in request:
            content_length = int(request['Content-Length'])

            if len(request['body']) < content_length:
                print("Attempting to retrieve {} ({} remaining) bytes of content".format(content_length, content_length - len(request['body'])))
                while len(request['body']) != content_length:
                    new_segment = connection_socket.recv(MAX_HTTP_MESSAGE_LENGTH).decode()
                    request['body'] += new_segment

        if request['path'] not in path_to_handler:
            print("{} not found in path_to_handler".format(request['path']))
            response = not_configured_response
        else:
            endpoint_handler = path_to_handler[request['path']]
            print("Path found. Passing to {}".format(endpoint_handler))
            response = endpoint_handler(**request)

        print("Sending response")

        connection_socket.send(response)
        connection_socket.close()
