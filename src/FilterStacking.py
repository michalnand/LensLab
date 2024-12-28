import numpy
import cv2



def bracketing(images, kernel_size = 11, min_accept = 0.05, max_accept = 0.95, temperature = 0.1):
    exposition_scores = []
    
    # for each image compute exposition score
    for n in range(len(images)):
        # convert to grayscale
        tmp       = cv2.cvtColor(images[n], cv2.COLOR_BGR2GRAY)

        # blured scores to avoid local errors
        expositon = cv2.GaussianBlur(tmp, (kernel_size,kernel_size), 0)
        expositon_score = numpy.abs(0.5 - expositon)

        penalty = numpy.where((expositon < min_accept) | (expositon > max_accept), 1.0, 0.0)

        exposition_scores.append(expositon_score + penalty)

    exposition_scores = numpy.array(exposition_scores)

    # softmax for weighted sum
    weights = numpy.exp(-exposition_scores/temperature)
    weights = weights/numpy.sum(weights, axis=0, keepdims=True)
    
    stacked_images = numpy.stack(images, axis=0)

    # compute the weighted sum
    result = numpy.sum(weights[..., None] * stacked_images, axis=0)

    #result[:, :, 0] = weights[0]
    #result[:, :, 1] = 0
    #result[:, :, 2] = weights[1]
   
    return result

def stacking(stacking_type, loader, idx, photos_count):
    
    if stacking_type in ["mean", "max", "min"]:
            
        result = loader[idx]

        height = result.shape[0]
        width  = result.shape[1]
        
        for n in range(1, photos_count):
            tmp = loader[n + idx]

            # resize if needed
            if tmp.shape[0] != height or tmp.shape[1] != width:
                tmp = cv2.resize(tmp, (width, height))

            if stacking_type == "mean":
                result+= tmp
            elif stacking_type == "max":
                result = numpy.maximum(result, tmp)
            elif stacking_type == "min":    
                result = numpy.minimum(result, tmp)

            print("processing image ", n, " from ", photos_count)

        if stacking_type == "mean":
            result = result/photos_count
        
    elif stacking_type == "median":
        if photos_count > 5:
            photos_count = 5
            print("median auto limited to ", photos_count, " photos")

        photos = []
        for n in range(photos_count):
            tmp = loader[n + idx]

            if n == 0:                
                height = tmp.shape[0]
                width  = tmp.shape[1]

            # resize if needed
            if tmp.shape[0] != height or tmp.shape[1] != width:
                tmp = cv2.resize(tmp, (width, height))

            photos.append(tmp)

            print("processing image ", n, " from ", photos_count)

        photos = numpy.array(photos)
        result = numpy.median(photos, axis=0)

    elif stacking_type == "bracketing":
        if photos_count > 5:
            photos_count = 5
            print("bracketing auto limited to ", photos_count, " photos")

        photos = []
        for n in range(photos_count):
            tmp = loader[n + idx]

            if n == 0:                
                height = tmp.shape[0]
                width  = tmp.shape[1]

            # resize if needed
            if tmp.shape[0] != height or tmp.shape[1] != width:
                tmp = cv2.resize(tmp, (width, height))

            photos.append(tmp)

            print("processing image ", n, " from ", photos_count)
        
        result = bracketing(photos)
    else:
        result = loader[idx].copy()
        print("unknown stacking : ", stacking_type)


    return result