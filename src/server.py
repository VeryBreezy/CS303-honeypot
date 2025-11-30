from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import subprocess
import time

def get_mac_from_ip(ip):
    subprocess.getoutput(f"ping -c 1 -W 1 {ip}")
    time.sleep(0.2)
    arp_output = subprocess.getoutput(f"arp -n {ip}")
    
    for part in arp_output.split():
        if ":" in part and len(part) == 17:
            return part.lower()
    return "Unknown"


class HoneypotHandler(BaseHTTPRequestHandler):

    def serve_file(self, filename, content_type="text/html"):
        with open(filename, "rb") as f:
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(f.read())

    def do_GET(self):
        clean_path = self.path.split("?")[0]
        client_ip = self.client_address[0]
        client_mac = get_mac_from_ip(client_ip)

        cookies = self.headers.get("Cookie", "")
        username = ""
        if "username=" in cookies:
            username = cookies.split("username=")[1].split(";")[0]

        print(f"GET path={clean_path} IP={client_ip} | MAC={client_mac}")

        if clean_path == "/" or clean_path == "/fake_website.html":
            self.serve_file("fake_website.html")

        elif clean_path == "/account":
            cookie_header = self.headers.get('Cookie', '')
            username = ""
            if 'username=' in cookie_header:
                username = cookie_header.split("username=")[1].split(";")[0]

            print(f"ACCOUNT ACCESS → User={username}, IP={client_ip}, MAC={client_mac}")

            if not username:
                # No cookie → not logged in
                self.serve_file("access_denied.html")
                return

            if self.check_identity(username, client_ip, client_mac):
                print("✔ Real user — showing account image")
                self.serve_file("account_picture.png", "image/png")
            else:
                print("⚠ Suspicious identity — stolen credentials")
                self.serve_file("suspicious.html")

        elif clean_path == "/accepted.html":
            self.serve_file("accepted.html")

        elif clean_path == "/suspicious.html":
            self.serve_file("suspicious.html")

        elif clean_path == "/access_denied.html":
            self.serve_file("access_denied.html")

        elif clean_path == "/access_denied.png":
            self.serve_file("access_denied.png", "image/png")

        else:
            self.send_error(404)

    def check_identity(self, username, client_ip, client_mac):
        with open("true_login.txt", "r") as auth_file:
            for line in auth_file:
                stored_user, stored_pass, stored_ip, stored_mac = line.strip().split(";")
                if username == stored_user:
                    return (client_ip == stored_ip and client_mac == stored_mac)
        return False

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            creds = urllib.parse.parse_qs(post_data.decode("utf-8"))

            username = creds.get("user", [""])[0]
            password = creds.get("pass", [""])[0]
            client_ip = self.client_address[0]
            client_mac = get_mac_from_ip(client_ip)

            print(f"LOGIN ATTEMPT: User={username} Password={password} IP={client_ip} MAC={client_mac}")

            authenticated = False
            mac_match = False

            with open("true_login.txt", "r") as auth_file:
                for line in auth_file:
                    stored_user, stored_pass, stored_ip, stored_mac = line.strip().split(";")
                    if username == stored_user and password == stored_pass:
                        authenticated = True
                        mac_match = (client_ip == stored_ip and client_mac == stored_mac)
                        break

            if authenticated:
                self.send_response(302)
                self.send_header("Content-type", "text/html")
                self.send_header("Set-Cookie", f"username={username}; Path=/")
                self.send_header("Location", "/accepted.html")
                self.end_headers()

            else:
                print("❌ Invalid login")
                self.serve_file("access_denied.html")
        else:
            self.send_error(404)


print("Server running on port 8080...")
server = HTTPServer(("0.0.0.0", 8080), HoneypotHandler)
server.serve_forever()