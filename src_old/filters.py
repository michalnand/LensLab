import cv2
import numpy


def global_brightness(x, level):
    return x + level

def global_contrast(x, level):
    mean_intensity = numpy.mean(x, axis=(0, 1), keepdims=True)
    result = (x - mean_intensity) * level + mean_intensity
    return result

def global_saturation(x, level):
    luminance = numpy.dot(x, [0.299, 0.587, 0.114])[..., numpy.newaxis]
    result = luminance + (x - luminance) * level
    return result

def adjust_ev(x, ev_change):
    ev_factor = 2 ** ev_change
    result = x * ev_factor
    return result

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

def _compute_colorfulness(x):
    R, G, B = x[:, :, 0], x[:, :, 1], x[:, :, 2]
    
    # Calculate differences
    rg = numpy.abs(R - G)
    gb = numpy.abs(G - B)
    br = numpy.abs(B - R)

    
    colorfulness = numpy.sqrt(rg**2 + gb**2 + br**2)
    return colorfulness



   

def local_saturation(x, level = 1.5, slope = 1.0, kernel_size = 11):
    #saturation   = _compute_saturation(x)
    colorfulness = _compute_colorfulness(x)

    #saturation_blur   = cv2.GaussianBlur(saturation, (kernel_size,kernel_size),0)
    colorfulness_blur = cv2.GaussianBlur(colorfulness, (kernel_size,kernel_size),0)

    #saturation_var   = cv2.GaussianBlur((saturation - saturation_blur)**2, (kernel_size, kernel_size), 0)
    #saturation_var   = numpy.sqrt(saturation_var)
    colorfulness_var = cv2.GaussianBlur((colorfulness - colorfulness_blur)**2, (kernel_size, kernel_size), 0)
    colorfulness_var = numpy.sqrt(colorfulness_var)

    colorfulness_var = numpy.clip(slope*colorfulness_var, 0.0, 1.0)
   

    adjusted_saturation = (1.0 - colorfulness_var)*level + colorfulness_var*1.0

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
    
    return balanced_image




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


def histogram_equalisation(image, strength):
   
    # Convert RGB to LAB for luminance processing
    lab_image = cv2.cvtColor((image * 255).astype(numpy.uint8), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab_image)

    # Perform histogram equalization on the L channel
    equalized_l = cv2.equalizeHist(l)

    # Blend the original and equalized L channels based on the strength
    blended_l = cv2.addWeighted(l.astype(numpy.float32), 1 - strength, 
                                equalized_l.astype(numpy.float32), strength, 0)

    # Recombine LAB channels and convert back to RGB    
    lab_image = cv2.merge((blended_l.astype(numpy.uint8), a, b))
    equalized_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2RGB)

    # Convert back to [0, 1] float32
    return equalized_image.astype(numpy.float32) / 255



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
