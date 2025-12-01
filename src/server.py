from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import subprocess
import time


def get_mac_from_ip(ip):
    subprocess.getoutput(f"ping -c 1 -W 1 {ip}")
    time.sleep(0.1)
    arp_output = subprocess.getoutput(f"arp -n {ip}")

    for part in arp_output.split():
        if ":" in part and len(part) == 17:
            return part.lower()
    return "Unknown"


class HoneypotHandler(BaseHTTPRequestHandler):

    def serve_file(self, filename, content_type="text/html"):
        """Helper to send a static file to client"""
        self.send_header("Content-type", content_type)
        self.end_headers()
        with open(filename, "rb") as f:
            self.wfile.write(f.read())

    def do_GET(self):
        clean_path = self.path.split("?")[0]
        cookies = self.headers.get("Cookie", "")

        print(f"GET {clean_path} | Cookies={cookies}")

        if clean_path == "/" or clean_path == "/website.html":
            self.send_response(200)
            self.serve_file("website.html")

        elif clean_path == "/accepted.html":
            self.send_response(200)
            self.serve_file("accepted.html")

        elif clean_path == "/account":
            if "session=valid" in cookies:
                print("Victim checking account, show picture")
                self.send_response(200)
                self.serve_file("account_picture.png", "image/png")
            elif "session=suspicious" in cookies:
                print("⚠ Suspicious session, show alert")
                self.send_response(200)
                self.serve_file("suspicious.html")
            else:
                print("No login session")
                self.send_response(200)
                self.serve_file("access_denied.html")

        elif clean_path == "/logout":
            print("Logout requested — cookie persists")
            self.send_response(302)
            self.send_header("Location", "/website.html")
            self.end_headers()

        elif clean_path == "/access_denied.html":
            self.send_response(200)
            self.serve_file("access_denied.html")

        elif clean_path == "/suspicious.html":
            self.send_response(200)
            self.serve_file("suspicious.html")

        elif clean_path == "/access_denied.png":
            self.send_response(200)
            self.serve_file("access_denied.png", "image/png")

        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            # Read POST credentials
            length = int(self.headers["Content-Length"])
            creds = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"))
            username = creds.get("user", [""])[0]
            password = creds.get("pass", [""])[0]
            client_ip = self.client_address[0]
            client_mac = get_mac_from_ip(client_ip)

            print(f"\n=== LOGIN ATTEMPT === {username} | IP={client_ip} | MAC={client_mac}")

            authenticated = False
            is_real_victim = False

            with open("true_login.txt", "r") as auth:
                for line in auth:
                    u, p, ip, mac = line.strip().split(";")
                    if username == u and password == p:
                        authenticated = True
                        is_real_victim = (client_ip == ip and client_mac == mac)
                        break

            if authenticated:
                session = "valid" if is_real_victim else "suspicious"
                print(f" SESSION STATUS = {session}")

                self.send_response(302)
                self.send_header("Set-Cookie", f"username={username}; Path=/")
                self.send_header("Set-Cookie", f"session={session}; Path=/")
                self.send_header("Location", "/accepted.html")
                self.end_headers()

            else:
                print("Invalid login credentials")
                self.send_response(200)
                self.serve_file("access_denied.html")

        else:
            self.send_error(404)


# Server Startup
print(" Honeypot Server running on port 8080...")
server = HTTPServer(("0.0.0.0", 8080), HoneypotHandler)
server.serve_forever()