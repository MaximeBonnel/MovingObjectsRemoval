import cv2
import numpy as np

# Variables
gamma = 3.5

contrast = 1
contrastRange = 200

darkening = 3
darkeningRange = 100

# Charger la vidéo
video_path = './IMG_8238T.MOV'
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

# Lire chaque image de la vidéo
while True:
    if not ret:
        break

    total_blue += frame[:, :, 0] * gamma
    total_green += frame[:, :, 1] * gamma
    total_red += frame[:, :, 2] * gamma
    
    frame_count += 1
    ret, frame = cap.read()

# Calculer les moyennes des canaux de couleur pour chaque position de pixel
average_blue = total_blue / frame_count
average_green = total_green / frame_count
average_red = total_red / frame_count

# Appliquer une correction gamma pour accentuer les couleurs claires
corrected_blue = np.power(average_blue, 1/gamma)
corrected_green = np.power(average_green, 1/gamma)
corrected_red = np.power(average_red, 1/gamma)

# Normaliser les valeurs des canaux corrigés entre 0 et 255
normalized_blue = (corrected_blue / np.max(corrected_blue)) * 255
normalized_green = (corrected_green / np.max(corrected_green)) * 255
normalized_red = (corrected_red / np.max(corrected_red)) * 255

# Créer une image finale avec les canaux corrigés
final_image = np.zeros((height, width, 3), dtype=np.float64)
final_image[:, :, 0] = normalized_blue
final_image[:, :, 1] = normalized_green
final_image[:, :, 2] = normalized_red

# Noircissement
for row in range(height):
    for col in range(width):
        if final_image[row, col, 0] < darkeningRange and final_image[row, col, 1] < darkeningRange and final_image[row, col, 2] < darkeningRange:
            final_image[row, col, 0] /= darkening
            final_image[row, col, 1] /= darkening
            final_image[row, col, 2] /= darkening

# Contraste
for row in range(height):
    for col in range(width):
        if final_image[row, col, 0] < contrastRange and final_image[row, col, 1] < contrastRange and final_image[row, col, 2] < contrastRange:
            final_image[row, col, 0] *= contrast
            final_image[row, col, 1] *= contrast
            final_image[row, col, 2] *= contrast

# Enregistrer l'image finale
output_path = './image_finale.png'
cv2.imwrite(output_path, final_image)

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()

print("Image finale enregistrée avec succès !")
