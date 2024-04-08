from MovingObjectsRemoval import MOR

video_path = './Videos/video3.MOV'
output_path = './Image/image_finale.png'

mor = MOR(video_path, output_path)
mor.Initialisation()
mor.Superposition()
mor.SaveImage()
mor.ShowImage()