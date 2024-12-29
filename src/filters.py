import cv2
import numpy


def global_brightness(x, level):
    return x + float(level)

def global_contrast(x, level):
    mean_intensity = numpy.mean(x, axis=(0, 1), keepdims=True)
    result = (x - mean_intensity) * float(level) + mean_intensity
    return result

def global_saturation(x, level):
    luminance = numpy.dot(x, [float(0.299), float(0.587),float(0.114)])[..., numpy.newaxis]
    result = luminance + (x - luminance) * level
    return result.astype(numpy.float32)

def adjust_ev(x, ev_change):
    ev_factor = 2 ** ev_change
    result = x * ev_factor
    return result


def adjust_ev_adaptive(x, ev_change, kernel_size = 11):
    luminance = numpy.dot(x, [float(0.299), float(0.587),float(0.114)])[..., numpy.newaxis]
    luminance_mean  = luminance.mean()
    luminance_local = cv2.GaussianBlur(luminance, (kernel_size, kernel_size), 0)


    d = (luminance_local - luminance_mean)/(luminance_mean + 1e-6)
    d = numpy.clip(d, 0.0, 1.0)

    d = numpy.expand_dims(d, 2)

    ev_change_tmp = ev_change*d
    result = adjust_ev(x, ev_change_tmp)

    return result.astype(numpy.float32)


def adjust_red(x, level):
    result = x.copy()
    result[:, :, 2]*= level
   
    return result

def adjust_green(x, level):
    result = x.copy()
    result[:, :, 1]*= level
   
    return result

def adjust_blue(x, level):
    result = x.copy()
    result[:, :, 0]*= level
   
    return result


def _compute_saturation(x):
    result = (numpy.max(x, 2) - numpy.min(x, 2))/(numpy.max(x, 2) + 10**-6)
    return result

def _compute_colorfulness(x, normalise = False):
    R, G, B = x[:, :, 0], x[:, :, 1], x[:, :, 2]
    
    # Calculate differences
    rg = numpy.abs(R - G)
    gb = numpy.abs(G - B)
    br = numpy.abs(B - R)

    colorfulness = numpy.sqrt(rg**2 + gb**2 + br**2)

    if normalise:
        norm = numpy.sqrt(R**2 + G**2 + B**2)
        colorfulness = colorfulness / (norm + 1e-8)
        
    return colorfulness



   
def local_saturation(x, level = 1.0, slope = 8.0, kernel_size = 11):
    colorfulness    = _compute_colorfulness(x, True)
    colorfulness    = cv2.GaussianBlur(colorfulness, (kernel_size,kernel_size),0)

    weight          = numpy.exp(-colorfulness*slope)
    
    adjusted_saturation = (1.0 - weight)*1.0 + weight*level

    adjusted_saturation = numpy.expand_dims(adjusted_saturation, 2)
    result = global_saturation(x, adjusted_saturation)

    return result

    


 # Convert Kelvin temperature to RGB scaling factors
def _kelvin_to_rgb(kelvin):
    # Clamp kelvin to range 1000K to 40000K
    kelvin = numpy.clip(kelvin, 1000, 40000) / 100
    
    # Compute red
    if kelvin <= 66:
        red = 255
    else:
        red = 329.698727446 * ((kelvin - 60) ** -0.1332047592)
        red = numpy.clip(red, 0, 255)
    
    # Compute green
    if kelvin <= 66:
        green = 99.4708025861 * numpy.log(kelvin) - 161.1195681661
        green = numpy.clip(green, 0, 255)
    else:
        green = 288.1221695283 * ((kelvin - 60) ** -0.0755148492)
        green = numpy.clip(green, 0, 255)
    
    # Compute blue
    if kelvin >= 66:
        blue = 255
    elif kelvin <= 19:
        blue = 0
    else:
        blue = 138.5177312231 * numpy.log(kelvin - 10) - 305.0447927307
        blue = numpy.clip(blue, 0, 255)
    
    return numpy.array([red, green, blue]) / 255  # Normalize to range 0–1

def adjust_white_balance(x, temperature = 6500):
   
    # Get scaling factors for the target Kelvin
    scaling_factors = _kelvin_to_rgb(temperature)


    # Normalize the scaling factors by the white point (e.g., D65 ~ 6500K)
    white_point = _kelvin_to_rgb(6500)
    compensation_factors = white_point / scaling_factors
   
    # Apply scaling factors to the image channels
    balanced_image = x * compensation_factors
    
    return balanced_image.astype(numpy.float32)




def adjust_clarity(image, strength, kernel_size = 11):
    # Convert to grayscale for detail emphasis
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Create a high-pass filter using a Gaussian blur
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    high_pass = gray - blurred  # Extract details
    high_pass = numpy.expand_dims(high_pass, 2)
    
    # Add weighted detail back into the original image
    enhanced = image + strength*high_pass

    return numpy.clip(enhanced, 0.0, 1.0, dtype=numpy.float32)


'''
def adjust_dehaze(image, strength, kernel_size = 11):
    # Compute the dark channel
    dark_channel = numpy.min(image, axis=2)  # Minimum across R, G, B channels
    dark_channel = cv2.erode(dark_channel, numpy.ones((kernel_size, kernel_size)))  # Local minima for haze
    
    # Softly estimate atmospheric light (weighted average of top dark channel pixels)
    flat_image = image.reshape(-1, 3)
    flat_dark = dark_channel.ravel()
    
    # Weighting mechanism: softmax of dark channel values
    top_percent = int(0.001 * len(flat_dark))  # Consider the top 0.1% darkest pixels
    weights = numpy.exp(flat_dark / 0.1)  # Exponential weights to emphasize brighter pixels
    weights /= weights.sum()  # Normalize weights
    
    atmospheric_light = numpy.dot(flat_image.T, weights).reshape(-1)  # Weighted sum
    
    # Estimate transmission map
    transmission = 1 - strength * (dark_channel / atmospheric_light.max())
    transmission = numpy.clip(transmission, 0.1, 1)  # Avoid complete blackness
    
    # Recover the image
    transmission = transmission[:, :, numpy.newaxis]
    dehazed = (image - atmospheric_light) / transmission + atmospheric_light
    return numpy.clip(dehazed, 0.0, 1.0)
'''



def adjust_dehaze(image, strength, kernel_size = 11):
    # Compute the dark channel
    dark_channel = numpy.min(image, axis=2)  # Minimum across R, G, B channels
    
    dark_channel = cv2.GaussianBlur(dark_channel, (kernel_size, kernel_size), 0)  # Local minima for haze
    
    # Softly estimate atmospheric light (weighted average of top dark channel pixels)
    flat_image = image.reshape(-1, 3)
    flat_dark = dark_channel.ravel()
    
    # Weighting mechanism: softmax of dark channel values
    weights = numpy.exp(flat_dark / 0.1)  # Exponential weights to emphasize brighter pixels
    weights /= weights.sum()  # Normalize weights
    
    atmospheric_light = numpy.dot(flat_image.T, weights).reshape(-1)  # Weighted sum
    
    # Estimate transmission map
    transmission = 1 - strength * (dark_channel / atmospheric_light.max())
    transmission = numpy.clip(transmission, 0.1, 1)  # Avoid complete blackness
    
    # Recover the image
    transmission = transmission[:, :, numpy.newaxis]
    dehazed = (image - atmospheric_light) / transmission + atmospheric_light
    return numpy.clip(dehazed, 0.0, 1.0)

'''
def guided_filter(I, p, kernel_size):
    mean_I  = cv2.boxFilter(I, cv2.CV_32F, (kernel_size, kernel_size))
    mean_p  = cv2.boxFilter(p, cv2.CV_32F, (kernel_size, kernel_size))
    mean_Ip = cv2.boxFilter(I * p, cv2.CV_32F, (kernel_size, kernel_size))


    cov_Ip = mean_Ip - mean_I * mean_p

    mean_II = cv2.boxFilter(I * I, cv2.CV_32F, (kernel_size, kernel_size))
    var_I = mean_II - mean_I * mean_I

    a = cov_Ip / (var_I + 1e-6)
    b = mean_p - a * mean_I

    mean_a = cv2.boxFilter(a, cv2.CV_32F, (kernel_size, kernel_size))
    mean_b = cv2.boxFilter(b, cv2.CV_32F, (kernel_size, kernel_size))

    return mean_a * I + mean_b

def adjust_dehaze(image, strength, kernel_size = 11):
    # Compute the dark channel
    # Minimum across R, G, B channels
    dark_channel = numpy.min(image, axis=2)  
    
    # Apply guided filter for smoother, edge-aware dark channel
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    dark_channel = guided_filter(gray_image, dark_channel, kernel_size)
    
    # Atmospheric light estimation (same as original)
    flat_image = image.reshape(-1, 3)
    flat_dark = dark_channel.ravel()
    weights = numpy.exp(flat_dark / 0.1)
    weights /= weights.sum()
    atmospheric_light = numpy.dot(flat_image.T, weights).reshape(-1)
    
    # Transmission map estimation
    transmission = 1 - strength * (dark_channel / atmospheric_light.max())
    transmission = numpy.clip(transmission, 0.1, 1)
    
    # Recover the image
    transmission = numpy.expand_dims(transmission, 2)
    dehazed = (image - atmospheric_light) / transmission + atmospheric_light
    return numpy.clip(dehazed, 0.0, 1.0, dtype=numpy.float32)
'''




def adjust_tones(image, dark_shift=0.0, mid_shift=0.0, light_shift=0.0):
    # define tone ranges
    dark_mask = image < 0.33
    mid_mask = (image >= 0.33) & (image < 0.67)
    light_mask = image >= 0.67
    
    # apply shifts to the respective tone ranges
    adjusted_image = numpy.zeros_like(image)
    adjusted_image[dark_mask]   = numpy.clip(image[dark_mask] + dark_shift, 0, 1)
    adjusted_image[mid_mask]    = numpy.clip(image[mid_mask] + mid_shift, 0, 1)
    adjusted_image[light_mask]  = numpy.clip(image[light_mask] + light_shift, 0, 1)
    
    return adjusted_image



def adjust_colors(image, red, green, blue): 
    # Convert RGB (0-1 range) to HSV
    #hsv = cv2.cvtColor((image * 255).astype(numpy.uint8), cv2.COLOR_RGB2HSV).astype(numpy.float32)
    #h, s, v = cv2.split(hsv)

    hsv = cv2.cvtColor((image * 255.0), cv2.COLOR_RGB2HSV).astype(numpy.float32)
    h, s, v = cv2.split(hsv)
    
    
    red_adjust   = red * (h < 60).astype(float)
    green_adjust = green * ((h >= 60) & (h < 120)).astype(float)
    blue_adjust  = blue * (h >= 120).astype(float)

    adjust = (red_adjust + green_adjust + blue_adjust)/3.0

    # Apply enhancements using the mask
    s = numpy.clip(s + adjust, 0, 255).astype(numpy.float32)
    
    
    # Merge back and convert to RGB
    enhanced_hsv = cv2.merge([h, s, v]) 
    enhanced_image = cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2RGB)
    
    # Normalize to range [0, 1]
    return (enhanced_image / 255.0).astype(numpy.float32)


def histogram_equalisation(image, strength):
   
    # Convert RGB to LAB for luminance processing
    lab_image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab_image)

    # Perform histogram equalization on the L channel   
    equalized_l = cv2.equalizeHist(l.astype(numpy.uint8)).astype(numpy.float32)
    equalized_l = numpy.clip(equalized_l, 0.0, 255.0)

    blended_l = (1.0 - strength)*l + strength*equalized_l
    blended_l = numpy.clip(blended_l, 0.0, 255.0)

    # Recombine LAB channels and convert back to RGB    
    lab_image = cv2.merge((blended_l, a, b))
    equalized_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2RGB)

    # Convert back to [0, 1] float32
    return equalized_image.astype(numpy.float32)



def blur_filter(image, strength, kernel_size = 17, sigma = 3.0):
    blurred = cv2.GaussianBlur(image, (kernel_size,kernel_size), sigma)
    result  = blurred*strength + (1.0 - strength)*image

    return result
   


def sharpen_filter(image, strength, kernel_size = 17, sigma = 3.0):
    blurred     = cv2.GaussianBlur(image, (kernel_size,kernel_size), sigma)
    sharpened   = image + strength * (image - blurred)  

    sharpened   = numpy.clip(sharpened, 0.0, 1.0)

    return sharpened



def bilateral_filter(image, strength, diameter=9, sigma_color=75, sigma_space=75):
    blurred = (image * 255).astype(numpy.float32)
    blurred = cv2.bilateralFilter(blurred, diameter, sigma_color, sigma_space)/255.0
    
    result  = blurred*strength + (1.0 - strength)*image

    return result



