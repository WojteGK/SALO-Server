import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json
from PIL import Image
import torch
import numpy as np

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']
        post_data = self.rfile.read(content_length)

        if content_type.startswith("image/"):
            # Save uploaded image temporarily
            filename = "uploaded_image.jpg"
            with open(filename, "wb") as file:
                file.write(post_data)

            # Process the image with YOLO
            try:
                detections = self.process_image(filename)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(detections).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error processing image: {str(e)}".encode())
            finally:
                # Clean up temporary file
                os.remove(filename)
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
        # Load and resize the image
        original_image = Image.open(image_path)
        width, height = original_image.size
        resized_image = original_image.resize((450, 450))
        resized_image_np = np.array(resized_image)

        # Run YOLO detection
        results = model(resized_image_np)

        # Extract detections
        detections = []
        for *xyxy, conf, cls in results.xyxy[0]:  # YOLOv5 uses `xyxy` format
            x_min, y_min, x_max, y_max = xyxy

            # Normalize coordinates to percentages of the resized image (450x450)
            x_min_norm = x_min / 450
            y_min_norm = y_min / 450
            x_max_norm = x_max / 450
            y_max_norm = y_max / 450

            # Store normalized bounding box in the response
            detections.append({
                "x_min": x_min_norm,
                "y_min": y_min_norm,
                "x_max": x_max_norm,
                "y_max": y_max_norm
            })

        # Return detections
        return {
            "original_width": width,
            "original_height": height,
            "detections": detections
        }


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


if __name__ == "__main__":
    # Load YOLOv5 model once at the start
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='runs/train/exp/weights/best.pt')  # Replace with your YOLOv5 model path
    run_server(port=8080)
