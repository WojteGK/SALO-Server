import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from email.parser import BytesParser
from email.policy import default
import urllib.parse
import json

import cv2
from PIL import Image
import torch
import numpy as np
import pandas as pd
import argparse

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_type = self.headers['Content-Type']

        # Check if it's a multipart form data request
        if content_type.startswith("multipart/form-data"):
            # Parse multipart data
            boundary = content_type.split("boundary=")[1].encode()
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # Use BytesParser to extract file content
            parts = BytesParser(policy=default).parsebytes(
                b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + body
            )

            # Find the file part
            for part in parts.iter_parts():
                if part.get_content_type().startswith("image/"):
                    # Save uploaded image temporarily
                    filename = "uploaded_image.jpg"
                    with open(filename, "wb") as file:
                        file.write(part.get_payload(decode=True))

                    # Process the image with YOLO
                    try:
                        grouped_detections = self.process_image(filename)
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(json.dumps(grouped_detections).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(f"Error processing image: {str(e)}".encode())
                    finally:
                        # Clean up temporary file
                        os.remove(filename)
                    return

            # If no image part is found, return an error
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No valid image file found.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Unsupported content type.")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Server is running. Ready to receive data.")

    def process_image(self, image_path):
        """
        Perform object detection on the image using YOLO.
        Returns a JSON-compatible response with normalized coordinates.
        """
        img = cv2.imread(image_path)
        results = model(img)

        print(results)
        return results.xyxy[0]


def get_device_ip():
    """
    Get the current device's IP address in the network.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address; doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def run_server(port=8080):
    ip = get_device_ip()
    print(f"Detected IP address: {ip}")
    server_address = (ip, port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting server on {ip}:{port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server.")
        httpd.server_close()

def perform_image_counting():
    return len([f for f in os.listdir(os.path.join(root, 'images')) if f.endswith(".bmp")])

if __name__ == "__main__":
    #ARGPARSER
    parser = argparse.ArgumentParser(description="Popopopopozdro kurwa twoja pierdolona mać")
    parser.add_argument('--path', type=str, help='Project root path')
    args = parser.parse_args()
    root = args.path

    #YOLO
    model_fname = [f for f in os.listdir(root) if f.endswith(".pt")][0]
    model_path = os.path.join(root, model_fname)
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)

    #PANDAS
    df = pd.read_csv(os.path.join(root, "data.csv"))

    #IMGS
    img_count = perform_image_counting()

    #RUN
    run_server(port=8080)
