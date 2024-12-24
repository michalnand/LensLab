import numpy
import cv2


def bracketing(images, kernel_size = 11, min_accept = 0.05, max_accept = 0.95):
    exposition_score = []
    
    # for each image compute exposition score
    for n in range(len(images)):
        # convert to grayscale
        tmp       = cv2.cvtColor(images[n], cv2.COLOR_BGR2GRAY)
        
        # compute if pixels within correnct range
        tmp       = (tmp > min_accept)*(tmp < max_accept)
        tmp       = numpy.array(tmp, dtype=numpy.float32)

        # blured scores to avoid local errors
        expositon = cv2.GaussianBlur(tmp, (kernel_size,kernel_size), 0)

        exposition_score.append(expositon)

    exposition_score = numpy.array(exposition_score) + 10e-6

    # normalize scores to create weights
    weights = exposition_score / numpy.sum(exposition_score, axis=0, keepdims=True)
    weights = numpy.exp(weights)
    weights = weights/numpy.sum(weights, axis=0, keepdims=True)
    
    stacked_images = numpy.stack(images, axis=0)
    
    # compute the weighted sum
    result = numpy.sum(weights[..., None] * stacked_images, axis=0)
   
    return result
