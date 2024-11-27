import os
import cv2
import torch
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

exp = "exp1" # Ustawienie modelu który został wyćwiczony (exp1/exp2...)
testImage = "test_2.jpg" # Ustawienie zdjecia do detekcji

base_dir = Path(__file__).resolve().parent

model_path = base_dir / "model" / "yolov5" / "runs" / "train" / exp / "weights" / "best.pt"
model = torch.hub.load( base_dir / "model" / "yolov5" ,'custom', path=model_path, source='local')

test_images_dir = base_dir / "model" / "SKU" / "images" / "test"
test_image_path = os.path.join(test_images_dir, testImage)

print("Ścieżka do obrazu testowego:", test_image_path)

def detect_objects(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print(f"Nie udało się wczytać obrazu: {image_path}")
        return None, None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = model(img)

    if results is not None:
        print(f"Liczba wykrytych obiektów: {len(results.xyxy[0])}")  # Wyniki w formacie [x1, y1, x2, y2, conf, class]
        print("Wyniki:", results.xyxy[0])
    else:
        print("Brak wyników.")

    results.render()  # Renderowanie wyników na obrazie
    return img, results

img, results = detect_objects(test_image_path)

if img is not None and results is not None:
    img = np.array(img, dtype=np.uint8)
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    plt.axis('off')
    plt.title('Wynik wykrywania obiektów')
    plt.show()
    output_image_path = 'wynik_wykrywania_obiektow.jpg'  # Zapisz obraz w głównym katalogu
    cv2.imwrite(output_image_path, img)  # Zapisz obraz
else:
    print("Wykrywanie obiektów nie powiodło się.")
