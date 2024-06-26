from MovingObjectsRemoval import MOR

video_path = './Videos/video3.MOV'
output_path = './Images/image_finale3.png'

mor = MOR(video_path, output_path)
mor.Stabilization()
mor.Initialisation()
mor.backgroundSubtraction()
mor.Superposition()
mor.SaveImage()
mor.ShowImage()