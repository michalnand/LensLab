import numpy
import cv2
from sklearn.cluster import KMeans

def _spatial_encoding(height, width):

    y = numpy.linspace(0, 1, width)
    x = numpy.linspace(0, 1, height)
    
    # Create the grid for the gradient
    x_grid, y_grid = numpy.meshgrid(x, y, indexing='ij')
    
    # Stack the x and y gradients to create the final encoding
    spatial_encoding = numpy.stack((x_grid, y_grid), axis=-1)
    
    return spatial_encoding


def _color_features(x, kernel_size):
    result = cv2.GaussianBlur(x, (kernel_size, kernel_size), 0)
    return result




def _edges_features(x, kernel_size = 7):

    grayscale = cv2.cvtColor(x, cv2.COLOR_RGB2GRAY)

    # Apply Sobel operator in horizontal (x) and vertical (y) directions
    sobel_x = cv2.Sobel(grayscale, cv2.CV_32F, dx=1, dy=0, ksize=3)
    sobel_y = cv2.Sobel(grayscale, cv2.CV_32F, dx=0, dy=1, ksize=3)

    # Stack the Sobel results into a 2-channel image
    sobel_edges = numpy.stack((sobel_x, sobel_y), axis=-1)

    smoothed = cv2.GaussianBlur(sobel_edges, (kernel_size, kernel_size), 0)

    return smoothed


def _compute_colorfulness(x, kernel_size):
    R, G, B = x[:, :, 0], x[:, :, 1], x[:, :, 2]
    
    # Calculate differences
    rg = numpy.abs(R - G)
    gb = numpy.abs(G - B)
    br = numpy.abs(B - R)

    colorfulness = numpy.sqrt(rg**2 + gb**2 + br**2)
    
    colorfulness = cv2.GaussianBlur(colorfulness, (kernel_size, kernel_size), 0)
    colorfulness = numpy.expand_dims(colorfulness, 2)
    return colorfulness

def _compute_image_features(x, kernel_size = 11):
    width = x.shape[1]
    height= x.shape[0]

    spatial_encoding = _spatial_encoding(height, width)
    color_features   = _color_features(x, kernel_size)
    edges_features   = _edges_features(x, kernel_size)
    colorfullness    = _compute_colorfulness(x, kernel_size)

   
    features = numpy.concatenate([spatial_encoding, color_features, edges_features, colorfullness], 2)
    return features

def _sky_ground_swap(image):
    x = numpy.array(image, numpy.float32)
    h = image.shape[0]
    upper_half = x[0:h//2].mean()
    lower_half = x[h//2:].mean()

    return upper_half < lower_half

def sky_detection(x, n_samples = 1000, scale_ratio = 4):
    x_resized   = cv2.resize(x, (x.shape[1]//scale_ratio, x.shape[0]//scale_ratio))

    features = _compute_image_features(x_resized)


    samples_y = numpy.random.randint(0, features.shape[0], n_samples)
    samples_x = numpy.random.randint(0, features.shape[1], n_samples)


    

    x_samples = features[samples_y, samples_x]


    print(">>> ", x_samples.shape)


    kmeans = KMeans(n_clusters=2, random_state=numpy.random.randint(5000))
    labels = kmeans.fit_predict(x_samples)

    centroids = kmeans.cluster_centers_

    tmp = numpy.expand_dims(centroids, 1)
    tmp = numpy.expand_dims(tmp, 2)
    d = features - tmp
    d = (d**2).sum(axis=-1)

    cluster_ids = numpy.argmin(d, axis=0)
    cluster_ids = numpy.array(cluster_ids, dtype=numpy.uint8)

    if _sky_ground_swap(cluster_ids):
        cluster_ids = 1-cluster_ids


    kernel = numpy.ones((3, 3), numpy.uint8) 
    cluster_ids = cv2.erode(cluster_ids, kernel, iterations=2)
    cluster_ids = numpy.array(cluster_ids*1.0, dtype=numpy.float32)

    #cluster_ids = cv2.GaussianBlur(cluster_ids, (19, 19), 0)

    cluster_ids = numpy.expand_dims(cluster_ids, 2)

    cluster_ids = (1.0 - cluster_ids)*x_resized 

    cv2.imshow("image", cluster_ids)
    cv2.waitKey(0)