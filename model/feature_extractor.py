import torch
from torchvision import models, transforms

# Wczytaj model ResNet do ekstrakcji cech
def load_feature_extractor():
    model = models.resnet50(pretrained=True)
    feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])  # Bez ostatniej warstwy klasyfikacyjnej
    feature_extractor.eval()
    return feature_extractor

# Funkcja do ekstrakcji embeddingu z obrazu
def get_embedding(image, model):
    preprocess = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = preprocess(image).unsqueeze(0)  # Dodanie wymiaru batch
    with torch.no_grad():
        embedding = model(image).flatten().numpy()
    return embedding