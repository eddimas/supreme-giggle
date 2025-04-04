import socket
import select
import socketserver
import http.server
from urllib.parse import urlparse
import logging
from requests_kerberos import HTTPKerberosAuth
from urllib.parse import urlparse

# Config
PROXY_HOST = 'my-proxy.example.com'
PROXY_PORT = 8080
UPSTREAM_PROXY = f'{PROXY_HOST}:{PROXY_PORT}'
BUFFER_SIZE = 8192

# Logging
logging.basicConfig(level=logging.DEBUG)

def generate_kerberos_token():
    try:
        auth = HTTPKerberosAuth()
        token = auth.generate_request_header(None, PROXY_HOST, is_preemptive=True)
        print(f"[DEBUG] Generated token: {token[:80]}...")
        return token
    except Exception as e:
        print(f"[ERROR] Kerberos token generation failed: {e}")
        return None

class KerberosProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        target_host, target_port = self.path.split(":")
        target_port = int(target_port)

        print(f"\n[+] CONNECT request to {self.path}")
        token = generate_kerberos_token()
        if not token:
            self.send_error(500, "Kerberos token generation failed")
            return

        try:
            proxy_sock = socket.create_connection((PROXY_HOST, PROXY_PORT))
            headers = (
                f"CONNECT {self.path} HTTP/1.1\r\n"
                f"Host: {self.path}\r\n"
                f"Proxy-Authorization: {token}\r\n"
                f"Proxy-Connection: Keep-Alive\r\n\r\n"
            )
            proxy_sock.sendall(headers.encode())
            response = proxy_sock.recv(BUFFER_SIZE)
            response_line = response.decode(errors='ignore').splitlines()[0]
            print(f"[DEBUG] Proxy response: {response_line}")

            if b"200 Connection Established" not in response:
                self.send_error(502, f"Tunnel failed: {response_line}")
                return

            self.send_response(200, "Connection Established")
            self.end_headers()
            self._tunnel_data(self.connection, proxy_sock)

        except Exception as e:
            print(f"[ERROR] CONNECT error: {e}")
            self.send_error(502, f"Tunnel failed: {e}")

    def _tunnel_data(self, client_socket, remote_socket):
        sockets = [client_socket, remote_socket]
        while True:
            rlist, _, _ = select.select(sockets, [], [])
            for s in rlist:
                data = s.recv(BUFFER_SIZE)
                if not data:
                    return
                if s is client_socket:
                    remote_socket.sendall(data)
                else:
                    client_socket.sendall(data)

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    PORT = 3129
    print(f"[+] Kerberos proxy running at http://localhost:{PORT}")
    print(f"[+] Forwarding through: {PROXY_HOST}:{PROXY_PORT}")
    with socketserver.ThreadingTCPServer(('', PORT), KerberosProxyHandler) as httpd:
        httpd.serve_forever()
