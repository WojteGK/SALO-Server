from object_detector import detect_objects
from feature_extractor import load_feature_extractor, get_embedding
from group_objects import group_and_visualize_kmeans, find_optimal_clusters_automatically, group_and_label
import numpy as np
import cv2
from sklearn.preprocessing import StandardScaler

def perform_clustering(image_path, max_clusters=10):
    # Wczytaj model do ekstrakcji cech
    feature_extractor = load_feature_extractor()

    # Wczytaj oryginalny obraz wejściowy (bez zaznaczeń)
    original_img = cv2.imread(image_path)
    if original_img is None:
        print(f"Nie udało się wczytać obrazu: {image_path}")
        return

    # Detekcja obiektów
    img_with_boxes, results = detect_objects(image_path)
    if img_with_boxes is None or results is None:
        print("Detekcja obiektów nie powiodła się.")
        return

    # Przygotowanie embeddingów i wyciętych obrazów
    boxes = results.xyxy[0].cpu().numpy()
    print(type(boxes))
    print(boxes)
    embeddings, cropped_images = [], []

    for box in boxes:
        x1, y1, x2, y2 = map(int, box[:4])  # Współrzędne bounding boxa
        cropped_img = original_img[y1:y2, x1:x2]  # Wytnij obiekt z oryginalnego obrazu
        cropped_images.append(cropped_img)

        obj_embedding = get_embedding(cropped_img, feature_extractor)  # Oblicz embedding
        embeddings.append(obj_embedding)

    # Normalizacja embeddingów
    embeddings = StandardScaler().fit_transform(np.array(embeddings))

    # Dynamiczny dobór liczby klastrów (metoda łokcia)
    optimal_clusters = find_optimal_clusters_automatically(embeddings, max_clusters)

    # Klasteryzacja i zapis do folderów
    # group_and_visualize_kmeans(embeddings, cropped_images, num_clusters=optimal_clusters)
    labels = group_and_label(embeddings, cropped_images, num_clusters=optimal_clusters)
    print(type(labels))

    boxes_with_labels = []
    for box, label in zip(boxes, labels):
        boxes_with_labels.append({
            "box": box,  # Współrzędne bounding boxa
            "group": int(label)  # Grupa przypisana przez K-Means
        })

    # Wyświetlenie przykładowego wyniku
    for item in boxes_with_labels:
        print(f"Box: {item['box']}, Group: {item['group']}")