import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']
        post_data = self.rfile.read(content_length)

        # Handle image uploads
        if content_type.startswith("image/"):
            filename = "uploaded_image.jpg"
            with open(filename, "wb") as file:
                file.write(post_data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Image received successfully.")
            print(f"Saved image as {filename}")
        # Handle text uploads
        elif content_type == "application/json":
            parsed_data = json.loads(post_data)
            print(f"Received JSON: {parsed_data}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Text received successfully.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Unsupported content type.")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Server is running. Ready to receive data.")

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server(port=8080)