import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
unique_path = base_dir / "model" / "SKU"

train_images_dir = os.path.join(unique_path, 'images\\train')
train_labels_dir = os.path.join(unique_path, 'labels\\train')

val_images_dir = os.path.join(unique_path, 'images\\val')
val_labels_dir = os.path.join(unique_path, 'labels\\val')

test_images_dir = os.path.join(unique_path, 'images\\test')
test_labels_dir = os.path.join(unique_path, 'labels\\test')

sku110k_path = os.path.join(unique_path, 'yolov5\\data\\sku110k.yaml')
with open(sku110k_path, 'w') as f:
    f.write(f"""
    train: {train_images_dir}
    val: {val_images_dir}

    nc: 1
    names: ['object']
    """)

# Najpierw odpalic main do stowrzenia pliku yaml

# Komenda do terminala:
# PODAC SWOJA SCIEZKE DO SKU110K.YAML!!!!!!!!!!!
# python train.py --img 300 --batch 8 --epochs 20 --data C:\Users\kusko\PycharmProjects\Model\yolov5\data\sku110k.yaml --weights yolov5s.pt