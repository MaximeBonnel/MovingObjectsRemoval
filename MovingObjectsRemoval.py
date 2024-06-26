import cv2
import numpy as np
from PIL import Image
from vidstab import VidStab, layer_overlay

# Correction courbe gamma
g = 1.5    # Facteur de correction gamma, supérieur à 1 pour accentuer les couleurs claires

# Seuil binaire

# Noircissement
darkening = 1
darkeningRange = 100

class MOR:

    def __init__(self, video_path, image_path):
        # Soustraction de fond
        self.bgSub = []

        # Valeurs de la vidéo
        self.video_path = video_path
        self.frame_count = 0

        # Valeurs de l'image finale
        self.image_path = image_path
        self.height = 0
        self.width = 0
        self.total_blue = None
        self.total_green = None
        self.total_red = None
        self.blue = None
        self.green = None
        self.red = None


    # Fonction de stabilisation de la vidéo
    def Stabilization(self):
        # Charger la vidéo
        cap = cv2.VideoCapture(self.video_path)

        # Capturer la première frame
        ret, frame = cap.read()
        self.height = frame.shape[0]
        self.width = frame.shape[1]

        # Compter le nombre de frames
        while True:
            if not ret:
                cap.release()
                break
            self.frame_count += 1
            ret, frame = cap.read()
        
        # "BRISK", "DENSE", "FAST"
        stabilizer = VidStab(kp_method='FAST')
        stabilizer.stabilize(input_path=self.video_path, 
                     output_path='stabilized_video.avi', 
                     border_type='black', 
                     border_size='auto',
                     smoothing_window=self.frame_count//2,
                     max_frames=self.frame_count//2,
                     layer_func=layer_overlay)
        self.video_path = './stabilized_video.avi'
        
    # Fonction d'initialisation pour charger la vidéo et initialiser les valeurs
    def Initialisation(self):
        # Charger la vidéo
        cap = cv2.VideoCapture(self.video_path)

        # Capturer la première frame
        ret, frame = cap.read()
        self.height = frame.shape[0]
        self.width = frame.shape[1]

        # Compter le nombre de frames
        while True:
            if not ret:
                cap.release()
                break
            self.frame_count += 1
            ret, frame = cap.read()

        # Initialiser les totaux des canaux de couleur pour chaque position de pixel
        self.total_blue = np.zeros((self.height, self.width), dtype=np.float64)
        self.total_green = np.zeros((self.height, self.width), dtype=np.float64)
        self.total_red = np.zeros((self.height, self.width), dtype=np.float64)

    # Appliquer le contraste
    #   alpha: Facteur de contraste, supérieur à 1 pour augmenter le contraste
    #   beta: Offset, généralement laissé à 0
    #   gamma: Facteur d'exposition, supérieur à 1 pour augmenter l'exposition
    def Editing(self, alpha=1, beta=0, gamma=1):
        # Charger la vidéo
        cap = cv2.VideoCapture(self.video_path)

        # Lire chaque image de la vidéo
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.release()
                break

            # Contraste
            contrasted_frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

            self.total_blue += contrasted_frame[:, :, 0] * gamma
            self.total_green += contrasted_frame[:, :, 1] * gamma
            self.total_red += contrasted_frame[:, :, 2] * gamma

        # Appliquer une correction gamma pour accentuer les couleurs claires
        """corrected_blue = np.power(average_blue, 1/g)
        corrected_green = np.power(average_green, 1/g)
        corrected_red = np.power(average_red, 1/g)"""

        # Noircissement
        """for row in range(height):
            for col in range(width):
                if final_image[row, col, 0] < darkeningRange and final_image[row, col, 1] < darkeningRange and final_image[row, col, 2] < darkeningRange:
                    final_image[row, col, 0] /= darkening
                    final_image[row, col, 1] /= darkening
                    final_image[row, col, 2] /= darkening"""

    def backgroundSubtraction(self):
        # Initialiser le soustracteur d'arrière-plan
        fgbg = cv2.createBackgroundSubtractorMOG2()

        cap = cv2.VideoCapture(self.video_path)

        while True:
            # Capturer une image depuis la webcam
            ret, frame = cap.read()
            if not ret:
                cap.release()
                break
            
            # Appliquer la soustraction d'arrière-plan
            fgmask = fgbg.apply(frame)
            
            # Ajouter le masque au tableau
            self.bgSub.append(fgmask)

    def Superposition(self):
        # Charger la vidéo
        cap = cv2.VideoCapture(self.video_path)
        count = 0

        # Lire chaque image de la vidéo
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.release()
                break

            # Completer totaux des canaux de couleur pour chaque position de pixel
            self.total_blue += frame[:, :, 0] - self.bgSub[count]
            self.total_green += frame[:, :, 1] - self.bgSub[count]
            self.total_red += frame[:, :, 2] - self.bgSub[count]

            count += 1

        # Calculer les moyennes des canaux de couleur pour chaque position de pixel
        avBlue = self.total_blue // self.frame_count
        avGreen = self.total_green // self.frame_count
        avRed = self.total_red // self.frame_count

        # Normaliser les valeurs des canaux corrigés entre 0 et 255
        self.blue = (avBlue / np.max(avBlue)) * 255
        self.green = (avGreen / np.max(avGreen)) * 255
        self.red = (avRed / np.max(avRed)) * 255

    def SaveImage(self):
        # Créer une image finale
        image = np.zeros((self.height, self.width, 3), dtype=np.float64)
        image[:, :, 0] = self.blue
        image[:, :, 1] = self.green
        image[:, :, 2] = self.red

        # Enregistrer l'image finale
        cv2.imwrite(self.image_path, image)
        print("Image finale enregistrée avec succès !")

    def ShowImage(self):
        # Afficher l'image finale
        image = Image.open(self.image_path)
        image.show()
