import numpy
import cv2
from sklearn.cluster import MeanShift, estimate_bandwidth


def _compute_colorfulness(x):
    R, G, B = x[:, :, 0], x[:, :, 1], x[:, :, 2]
    
    # Calculate differences
    rg = numpy.abs(R - G)
    gb = numpy.abs(G - B)
    br = numpy.abs(B - R)

    colorfulness = numpy.sqrt(rg**2 + gb**2 + br**2)
    return colorfulness


def _spatial_encoding(height, width):

    y = numpy.linspace(0, 1, width)/width
    x = numpy.linspace(0, 1, height)/height
    
    # Create the grid for the gradient
    x_grid, y_grid = numpy.meshgrid(x, y, indexing='ij')
    
    # Stack the x and y gradients to create the final encoding
    spatial_encoding = numpy.stack((x_grid, y_grid), axis=-1)
    
    return spatial_encoding


def _compute_image_features(x, kernel_size = 11):
    kernel = numpy.ones((kernel_size,kernel_size),numpy.float32)/(kernel_size**2)

    y = cv2.cvtColor(x, cv2.COLOR_BGR2LAB)
    y = cv2.filter2D(y, -1, kernel)

    spatial_encoding = _spatial_encoding(x.shape[0], x.shape[1])

    features = numpy.concatenate([y, spatial_encoding], 2)
    return features
    
   

def _create_colors(n_colors):
    result = numpy.zeros((n_colors, 3))

    for n in range(n_colors):
        theta = 2.0*numpy.pi*n/n_colors
        result[n, 0] = (numpy.sin(theta + (0.0/3.0)*2.0*numpy.pi) + 1.0)/2.0
        result[n, 1] = (numpy.sin(theta + (1.0/3.0)*2.0*numpy.pi) + 1.0)/2.0
        result[n, 2] = (numpy.sin(theta + (2.0/3.0)*2.0*numpy.pi) + 1.0)/2.0

    return result

def segmentation(x, n_samples = 1000):


    features  = _compute_image_features(x)

    samples_y = numpy.random.randint(0, features.shape[0], n_samples)
    samples_x = numpy.random.randint(0, features.shape[1], n_samples)

    x_samples = features[samples_y, samples_x]


    bandwidth = estimate_bandwidth(x_samples, quantile=0.2, n_samples=n_samples)

    ms_model = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms_model.fit(x_samples)

    labels = ms_model.labels_
    centroids = ms_model.cluster_centers_

    n_clusters = numpy.max(labels) + 1

    tmp = numpy.expand_dims(centroids, 1)
    tmp = numpy.expand_dims(tmp, 2)
    d = features - tmp
    d = (d**2).sum(axis=-1)

    cluster_ids = numpy.argmin(d, axis=0)


    colors = _create_colors(n_clusters)

    result = colors[cluster_ids]

    return result
