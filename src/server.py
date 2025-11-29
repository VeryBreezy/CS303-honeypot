from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

#The imports are based on what we need for the server to work on http for the class
#This is what holds the server for the fake_website html to be able to do requests and answer them.

print("Beginning server start")
class HoneypotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("GET path:", self.path)   # DEBUG LINE
        if self.path.startswith("/") and ("fake_website.html" in self.path or self.path == "/"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("fake_website.html", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/access_denied.png":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open("access_denied.png", "rb") as img:
                self.wfile.write(img.read())
        elif self.path == "/access_denied.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            print("IM PRINTGINGGGG")
            print(self.path)
            with open("access_denied.html", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/login":
            # Suspicious: trying to access POST page without form submission
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>ACCESS DENIED</h2><p>Suspicious behavior detected.</p>")

        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            creds = urllib.parse.parse_qs(post_data.decode('utf-8'))

            username = creds.get("user", [""])[0]
            password = creds.get("pass", [""])[0]

            # Log ALL attempts
            with open("creds.txt", "a") as log:
                log.write(f"Username: {username} Password: {password}\n")
            print(username)
            print(password)
            # Check against allowed credentials
            authenticated = False
            with open("login.txt", "r") as auth_file:
                for line in auth_file:
                    stored_user, stored_pass = line.strip().split(":")
                    if username == stored_user and password == stored_pass:
                        authenticated = True
                        break

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            if authenticated:
                self.wfile.write(b"<h2>Welcome!</h2><p>Valid login.</p>")
            else:
                with open("access_denied.html", "rb") as f:
                    self.wfile.write(f.read())


server = HTTPServer(("0.0.0.0", 8080), HoneypotHandler)
print("Server running on port 8080...")
server.serve_forever()