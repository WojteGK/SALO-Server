from sklearn.cluster import KMeans
from kneed import KneeLocator
from pathlib import Path
from collections import Counter
import shutil
import cv2
# Znajduje optymalną liczbę klastrów metodą "łokcia".
def find_optimal_clusters_automatically(embeddings, max_clusters=20):
    inertia = [] # Lista na wartości inercji (wewnątrzgrupowej odległości).
    for n in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=n, random_state=42)
        kmeans.fit(embeddings)
        inertia.append(kmeans.inertia_)
    # Wykrywanie punktu "łokcia".
    kneedle = KneeLocator(range(1, max_clusters + 1), inertia, curve="convex", direction="decreasing")
    optimal_clusters = kneedle.knee or 2  # Domyślnie ustawiamy 2, jeśli brak łokcia.
    print(f"Optymalna liczba grup: {optimal_clusters}")
    return optimal_clusters

# Grupowanie obiektów za pomocą K-Means i zapis do folderów.
def group_and_visualize_kmeans(embeddings, cropped_images, output_dir="GROUPS", num_clusters=10):
    output_path = Path(output_dir)
    if output_path.exists(): # Jeśli folder wynikowy istnieje, usuń go, by uniknąć konfliktów.
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Dopasowanie modelu K-Means i przypisanie etykiet.
    kmeans = KMeans(n_clusters=num_clusters, init='k-means++', n_init=10, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    # Wyświetlenie liczby obiektów w każdej grupie.
    counts = Counter(labels)
    print("Liczba obiektów w grupach (K-Means):")
    for cluster, count in sorted(counts.items()):
        print(f"Grupa {cluster + 1}: {count} obiektów")

    # Zapisanie obrazów do folderów odpowiadających grupom.
    for i in range(num_clusters):
        cluster_dir = output_path / f"Group_{i + 1}"
        cluster_dir.mkdir(parents=True, exist_ok=True)
        cluster_images = [cropped_images[j] for j in range(len(labels)) if labels[j] == i]

        for idx, obj_image in enumerate(cluster_images):
            if obj_image is not None and obj_image.size != 0:
                output_image_path = cluster_dir / f"object_{idx + 1}.jpg"
                cv2.imwrite(str(output_image_path), obj_image)

    print(f"Wyniki zapisano w folderze: {output_path}")
