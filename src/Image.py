import numpy
import cv2

import filters

class Image:

    def __init__(self, image_full):
        self.image_orig = image_full.copy()

        self.image_orig_small   = cv2.resize(self.image_orig, (self.image_orig.shape[1]//8, self.image_orig.shape[0]//8))
        self.image_curr         = self.image_orig_small.copy()

        self.update_histogram()

        self.ev_default = 0.0
        self.ev_min  = -4.0
        self.ev_max  = 4.0
        self.ev_curr = 0.0


        self.temperature_default = 6500.0
        self.temperature_min  = 2000.0
        self.temperature_max  = 20000.0
        self.temperature_curr = 6500.0  

        self.brightness_default = 0.0
        self.brightness_min = -1.0
        self.brightness_max = 1.0
        self.brightness_curr= 0.0

        self.contrast_default = 1.0
        self.contrast_min = 0.0
        self.contrast_max = 5.0
        self.contrast_curr= 1.0


        self.saturation_default = 1.0
        self.saturation_min = 0.0
        self.saturation_max = 4.0
        self.saturation_curr= 1.0

        self.vibrance_default = 1.0
        self.vibrance_min = 0.0
        self.vibrance_max = 4.0
        self.vibrance_curr= 1.0

    def get_image(self):
        return self.image_curr
    
    def get_histogram(self):
        return self.histogram
    
    def get_ev(self):
        return self.ev_min, self.ev_max, self.ev_curr
    
    def get_temperature(self):
        return self.temperature_min, self.temperature_max, self.temperature_curr
    
    def get_brightness(self):
        return self.brightness_min, self.brightness_max, self.brightness_curr 
    
    def get_contrast(self):
        return self.contrast_min, self.contrast_max, self.contrast_curr 
    
    def get_saturation(self):
        return self.saturation_min, self.saturation_max, self.saturation_curr 
    
    def get_vibrance(self):
        return self.vibrance_min, self.vibrance_max, self.vibrance_curr 
    

    
    def set_default(self):
        self.ev_curr = self.ev_default
        self.brightness_curr = self.brightness_default
        self.contrast_curr = self.contrast_default
        self.saturation_curr = self.saturation_default
        self.vibrance_curr = self.vibrance_default
        self._update()

    def set_ev(self, value):
        self.ev_curr = value    
        self._update()

    def set_temperature(self, value):
        self.temperature_curr = value    
        self._update()

    def set_brightness(self, value):
        self.brightness_curr = value
        self._update()

    def set_contrast(self, value):
        self.contrast_curr = value
        self._update()

    def set_saturation(self, value):
        self.saturation_curr = value
        self._update()

    def set_vibrance(self, value):
        self.vibrance_curr = value
        self._update()  

    def _update(self):
        x = self.image_orig_small.copy()
        x = filters.adjust_ev(x, self.ev_curr)
        x = filters.adjust_white_balance(x, self.temperature_curr)
        
        x = filters.global_brightness(x, self.brightness_curr)
        x = filters.global_contrast(x, self.contrast_curr)
        x = filters.global_saturation(x, self.saturation_curr)
        x = filters.local_saturation(x, self.vibrance_curr)

        x = numpy.clip(x, 0.0, 1.0)

        self.image_curr = x 

        self.update_histogram()

        print("setting to ", self.ev_curr, self.temperature_curr, self.brightness_curr, self.contrast_curr)

    def update_histogram(self): 
        #tmp = cv2.resize(self.image_curr, (self.image_curr.shape[1]//16, self.image_curr.shape[0]//16))   
        tmp = numpy.array(self.image_curr*255, dtype=numpy.uint8)

        self.histogram = numpy.zeros((4, 256))


        r = cv2.calcHist([tmp], [0], None, [256], [0, 256])[:, 0]
        g = cv2.calcHist([tmp], [1], None, [256], [0, 256])[:, 0]
        b = cv2.calcHist([tmp], [2], None, [256], [0, 256])[:, 0]
            
        self.histogram[0] = r + g + b
        self.histogram[1] = r
        self.histogram[2] = g
        self.histogram[3] = b


