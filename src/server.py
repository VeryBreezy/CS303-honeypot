from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import subprocess
import time

def get_mac_from_ip(ip):
    subprocess.getoutput(f"ping -c 1 -W 1 {ip}")
    time.sleep(0.2)
    arp_output = subprocess.getoutput(f"arp -n {ip}")
    print("ARP cmd output:", arp_output)
    
    parts = arp_output.split()
    for part in parts:
        if ":" in part and len(part) == 17:
            return part.lower()
    return "Unknown"

print("Beginning server start")

class HoneypotHandler(BaseHTTPRequestHandler):

    def serve_file(self, filename, content_type="text/html"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        with open(filename, "rb") as f:
            self.wfile.write(f.read())

    def do_GET(self):
        print("GET path:", self.path)

        clean_path = self.path.split("?")[0]  # Remove everything after ?

        if clean_path == "/" or clean_path == "/fake_website.html":
            self.serve_file("fake_website.html")
        elif clean_path == "/accepted.html":
            self.serve_file("accepted.html")
        elif clean_path == "/access_denied.html":
            self.serve_file("access_denied.html")
        elif clean_path == "/suspicious.html":
            self.serve_file("suspicious.html")
        elif clean_path == "/access_denied.png":
            self.serve_file("access_denied.png", "image/png")
        elif clean_path == "/fake_accepted.html":
            self.serve_file("fake_accepted.html")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            creds = urllib.parse.parse_qs(post_data.decode("utf-8"))

            username = creds.get("user", [""])[0]
            password = creds.get("pass", [""])[0]
            client_ip = self.client_address[0]
            client_mac = get_mac_from_ip(client_ip)

            print("\n====== LOGIN ATTEMPT ======")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"IP: {client_ip}")
            print(f"MAC: {client_mac}")

            with open("logs.txt", "a") as log:
                log.write(f"{username}:{password} IP={client_ip} MAC={client_mac}\n")

            authenticated = False
            mac_match = False

            with open("true_login.txt", "r") as auth_file:
                for line in auth_file:
                    stored_user, stored_pass, stored_ip, stored_mac = line.strip().split(";")
                    if username == stored_user and password == stored_pass:
                        authenticated = True
                        if client_ip == stored_ip and client_mac == stored_mac:
                            mac_match = True
                        break

            if authenticated and mac_match:
                print("Legit login — Correct identity")
                self.serve_file("accepted.html")

            elif authenticated and not mac_match:
                print("STOLEN CREDENTIALS DETECTED — Wrong device")
                self.serve_file("fake_accepted.html")

            else:
                print("Invalid login attempt")
                self.serve_file("access_denied.html")

        else:
            self.send_error(404)


server = HTTPServer(("0.0.0.0", 8080), HoneypotHandler)
print("Server running on port 8080...")
server.serve_forever()