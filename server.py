import csv
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from email.parser import BytesParser
from email.policy import default
import urllib.parse
import json
from copy import deepcopy

from object_detector import detect_objects
from feature_extractor import load_feature_extractor, get_embedding
from group_objects import group_and_visualize_kmeans, find_optimal_clusters_automatically, group_and_label
import numpy as np
from sklearn.preprocessing import StandardScaler

import cv2
from PIL import Image
import torch
import pandas as pd
import argparse

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_type = self.headers['Content-Type']

        if self.path == '/assignments':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            try:
                # Parse JSON data
                data = json.loads(body)
                data = json.loads(data)
                print(data)
                print(type(data))
                id = data['id'].strip('.bmp')

                groupped_detections = json.loads(open(f"{os.path.join(root, 'images', id)}.json").read())
                groupped_counts = {}
                for key, value in groupped_detections.items():
                    groupped_counts[key] = len(value)

                for key, value in data['assignments'].items():
                    if key != 'id':
                        df.loc[df['alias'] == value, 'count'] += groupped_counts[str(key)]

                df.to_csv(os.path.join(root, "data.csv"), index=False)
                if not os.path.exists(os.path.join(root, 'cache')):
                    os.makedirs(os.path.join(root, 'cache'))
                counter = len(os.listdir(os.path.join(root, 'cache')))
                df.to_csv(os.path.join(root, 'cache', f'{counter}.csv'), index=False)

                # Send response
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "good"}).encode())

            except json.JSONDecodeError:
                # Handle invalid JSON
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON data"}).encode())

        if self.path == '/':
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
                        filename = f"{os.path.join(root, 'images', str(img_count))}.bmp"
                        with open(filename, "wb") as file:
                            file.write(part.get_payload(decode=True))

                        # Process the image with YOLO
                        try:
                            grouped_detections = self.process_image(filename)
                            group_names = []
                            csvfile = os.path.join(root, 'data.csv')
                            with open(csvfile,'r') as csvfile:
                                data = csv.reader(csvfile, delimiter=',')
                                next(data)

                                for row in data:
                                    group_names.append(row[1])

                            just_file_id = os.path.basename(filename)

                            response_data = {
                                "detections": grouped_detections,
                                "groups": group_names,
                                "id": just_file_id
                            }

                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(json.dumps(response_data).encode())
                            with open(filename.replace(".bmp", ".json"), "w") as file:
                                json.dump(grouped_detections, file)
                        except Exception as e:
                            self.send_response(500)
                            self.end_headers()
                            self.wfile.write(f"Error processing image: {str(e)}".encode())
                        #finally:
                            # Clean up temporary file
                            # os.remove(filename)
                        perform_image_counting()
                        return

                # If no image part is found, return an error
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No valid image file found.")
            else:
                # Unsupported content type
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
        boxes = results.xyxy[0].cpu().numpy()

        embeddings, cropped_images = [], []

        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])  # Współrzędne bounding boxa
            cropped_img = img[y1:y2, x1:x2]  # Wytnij obiekt z oryginalnego obrazu
            cropped_images.append(cropped_img)

            obj_embedding = get_embedding(cropped_img, feature_extractor)  # Oblicz embedding
            embeddings.append(obj_embedding)

        # Normalizacja embeddingów
        embeddings = StandardScaler().fit_transform(np.array(embeddings))

        # Dynamiczny dobór liczby klastrów (metoda łokcia)
        optimal_clusters = find_optimal_clusters_automatically(embeddings) #TODO: find optimal number of clusters

        # Klasteryzacja i zapis do folderów
        # group_and_visualize_kmeans(embeddings, cropped_images, num_clusters=optimal_clusters)
        labels = group_and_label(embeddings, cropped_images, num_clusters=optimal_clusters)

        wajchens_dict = {}

        for idx, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box[:4])
            group = int(labels[idx])
            if group not in wajchens_dict:
                wajchens_dict[group] = []
            wajchens_dict[group].append({"x1": x1,"y1": y1, "x2": x2, "y2": y2})

        return wajchens_dict


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

    #RESNET
    feature_extractor = load_feature_extractor()

    #PANDAS
    df = pd.read_csv(os.path.join(root, "data.csv"))

    #IMGS
    img_count = perform_image_counting()

    #RUN
    run_server(port=8080)
