import torch
import cv2
from pathlib import Path


def detect_objects(image_path, model_path=None, exp="exp"):
    """
    Wykonuje detekcję obiektów za pomocą YOLOv5.
    :param model_path: Ścieżka do wag YOLOv5. Jeśli None, używa domyślnej.
    :return: Obraz z zaznaczeniami i wyniki detekcji.
    """
    try:
        base_dir = Path(__file__).resolve().parent
        model_path = model_path or base_dir / "yolov5" / "runs" / "train" / exp / "weights" / "best.pt"
        yolov5_path = base_dir / "yolov5"
        model = torch.hub.load(str(yolov5_path), 'custom', path=str(model_path), source='local')
    except Exception as e:
        print(f"Błąd podczas ładowania modelu YOLOv5: {e}")
        return None, None

    img = cv2.imread(image_path)
    if img is None:
        print(f"Nie udało się wczytać obrazu: {image_path}")
        return None, None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = model(img)

    if results is not None and len(results.xyxy[0]) > 0:
        print(f"Detekcja zakończona. Liczba wykrytych obiektów: {len(results.xyxy[0])}")

        results.render()  # Dodaje ramki na obraz wejściowy
        img_with_boxes = results.ims[0]
        output_path = Path(image_path).parent / "wynik_detekcji.jpg"
        cv2.imwrite(str(output_path), cv2.cvtColor(img_with_boxes, cv2.COLOR_RGB2BGR))

        print(f"Wynik detekcji zapisany w: {output_path}")
        return img_with_boxes, results
    else:
        print("Brak wyników detekcji.")
        return None, None

