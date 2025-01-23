import torch
from torchvision import models, transforms

# Wczytaj model ResNet do ekstrakcji cech
def load_feature_extractor():

    model = models.resnet50(pretrained=True) # Wczytanie pretrenowanego modelu ResNet50
    feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])  # Bez ostatniej warstwy klasyfikacyjnej
    feature_extractor.eval() # Ustawienie modelu w tryb ewaluacji (nie trenujemy go)
    return feature_extractor

# Funkcja do ekstrakcji embeddingu z obrazu
def get_embedding(image, model):
    """
    Ekstrakcja wektora cech (embeddingu) z pojedynczego obrazu za pomocą podanego modelu.

    :param image: Obraz w formacie NumPy lub podobnym (np. wynik cv2.imread()).
    :param model: Model PyTorch używany do ekstrakcji cech.
    :return: Wektor cech (embedding) w formie jednowymiarowej tablicy NumPy.
    """
    preprocess = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)), # Zmiana rozmiaru obrazu na 224x224 (zgodnie z wymaganiami ResNet)
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), # Normalizacja obrazu
    ])
    image = preprocess(image).unsqueeze(0)  # Dodanie wymiaru batch
    with torch.no_grad(): # Wyłączenie gradientów, bo nie trenujemy modelu
        embedding = model(image).flatten().numpy() # Ekstrakcja cech i spłaszczenie do 1D
    return embedding