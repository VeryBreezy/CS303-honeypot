from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

#The imports are based on what we need for the server to work on http for the class
#This is what holds the server for the fake_website html to be able to do requests and answer them.
class HoneypotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/fake_website.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("fake_website.html", "rb") as file:
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

            username = creds.get("username", [""])[0]
            password = creds.get("password", [""])[0]

            # Log stolen credentials
            with open("creds.txt", "a") as log:
                log.write(f"Username: {username}, Password: {password}\n")

            # Send success response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Login Successful!</h2><p>You are logged in.</p>")
        else:
            self.send_error(404)