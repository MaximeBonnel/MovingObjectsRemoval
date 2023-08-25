import cv2
import numpy as np
from PIL import Image

#################### MODE ####################
AverageMode = 1
SuperpositionMode = 0

   ########################################

# Contraste
alpha = 1  # Facteur de contraste, supérieur à 1 pour augmenter le contraste
beta = 0    # Offset, généralement laissé à 0

# Exposition
gamma = 1 # Facteur d'exposition, supérieur à 1 pour augmenter l'exposition

# Correction courbe gamma
g = 1.5    # Facteur de correction gamma, supérieur à 1 pour accentuer les couleurs claires

# Seuil binaire

# Noircissement
darkening = 1
darkeningRange = 100

# Charger la vidéo
video_path = './Videos/video3.MOV'
cap = cv2.VideoCapture(video_path)

# Capturer la première frame
ret, frame = cap.read()
height = frame.shape[0]
width = frame.shape[1]

# Initialiser les totaux des canaux de couleur pour chaque position de pixel
total_blue = np.zeros((height, width), dtype=np.float64)
total_green = np.zeros((height, width), dtype=np.float64)
total_red = np.zeros((height, width), dtype=np.float64)
frame_count = 0

# Moyenne des pixels
if AverageMode == 1:
    # Lire chaque image de la vidéo
    while True:
        if not ret:
            break

        # Contraste
        contrasted_frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

        total_blue += contrasted_frame[:, :, 0] * gamma
        total_green += contrasted_frame[:, :, 1] * gamma
        total_red += contrasted_frame[:, :, 2] * gamma
        
        frame_count += 1
        ret, frame = cap.read()

    # Calculer les moyennes des canaux de couleur pour chaque position de pixel
    average_blue = total_blue / frame_count
    average_green = total_green / frame_count
    average_red = total_red / frame_count

# Pixels les plus clairs
if SuperpositionMode == 1:
    # Lire chaque image de la vidéo
    while True:
        if not ret:
            break

        # Contraste
        contrasted_frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

        # Parcourir chaque pixel de l'image
        for y in range(height):
            for x in range(width):
                if (contrasted_frame[y, x, 0] > total_blue[y, x] and contrasted_frame[y, x, 1] > total_green[y, x] and contrasted_frame[y, x, 2] > total_red[y, x]):
                    total_blue[y, x] = contrasted_frame[y, x, 0] * gamma
                    total_green[y, x] += contrasted_frame[y, x, 1] * gamma
                    total_red[y, x] += contrasted_frame[y, x, 2] * gamma

        ret, frame = cap.read()

        average_blue = total_blue
        average_green = total_green
        average_red = total_red

# Appliquer une correction gamma pour accentuer les couleurs claires
corrected_blue = np.power(average_blue, 1/g)
corrected_green = np.power(average_green, 1/g)
corrected_red = np.power(average_red, 1/g)

# Noircissement
"""for row in range(height):
    for col in range(width):
        if final_image[row, col, 0] < darkeningRange and final_image[row, col, 1] < darkeningRange and final_image[row, col, 2] < darkeningRange:
            final_image[row, col, 0] /= darkening
            final_image[row, col, 1] /= darkening
            final_image[row, col, 2] /= darkening"""

# Normaliser les valeurs des canaux corrigés entre 0 et 255
normalized_blue = (corrected_blue / np.max(corrected_blue)) * 255
normalized_green = (corrected_green / np.max(corrected_green)) * 255
normalized_red = (corrected_red / np.max(corrected_red)) * 255

# Créer une image finale avec les canaux corrigés
image = np.zeros((height, width, 3), dtype=np.float64)
image[:, :, 0] = normalized_blue
image[:, :, 1] = normalized_green
image[:, :, 2] = normalized_red

# Enregistrer l'image finale
output_path = './Image/image_finale.png'
cv2.imwrite(output_path, image)

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()

print("Image finale enregistrée avec succès !")

image = Image.open("./Image/image_finale.png")
image.show()
