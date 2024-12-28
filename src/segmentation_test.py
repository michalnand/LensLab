from SkyDetection import *
from ImageLoader import *


if __name__ == "__main__":
    loader = ImageLoader("../testing_images/testing_images_e/")

    image = loader[3]

    print(image.shape)

    sky_detection(image)
