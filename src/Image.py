import numpy
import cv2
import json
import os

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
        self.temperature_min     = 2000.0
        self.temperature_max     = 20000.0
        self.temperature_curr    = 6500.0  

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

        self.tones_default = 0.0
        self.tones_min     = -0.1
        self.tones_max     = 0.1
        self.shadows_curr  = 0.0
        self.midtones_curr = 0.0
        self.highlight_curr= 0.0


        self.equalisation_default = 0.0
        self.equalisation_min = 0.0
        self.equalisation_max = 1.0
        self.equalisation_curr= 0.0

        self.split_preview = 0

   

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
    
    def get_tones(self):
        return self.tones_min, self.tones_max, self.shadows_curr, self.midtones_curr, self.highlight_curr
    
    def get_equalisation(self):
        return self.equalisation_min, self.equalisation_max, self.equalisation_curr 
    

    
    def set_default(self):
        self.ev_curr = self.ev_default
        self.brightness_curr = self.brightness_default
        self.contrast_curr = self.contrast_default
        self.saturation_curr = self.saturation_default
        self.vibrance_curr = self.vibrance_default
        self.update()

    def set_ev(self, value):
        self.ev_curr = value    
        self.update()

    def set_temperature(self, value):
        self.temperature_curr = value    
        self.update()

    def set_brightness(self, value):
        self.brightness_curr = value
        self.update()

    def set_contrast(self, value):
        self.contrast_curr = value
        self.update()

    def set_saturation(self, value):
        self.saturation_curr = value
        self.update()

    def set_vibrance(self, value):
        self.vibrance_curr = value
        self.update() 

    def set_tones(self, shadows_curr, midtones_curr, highlight_curr):
        self.shadows_curr    = shadows_curr
        self.midtones_curr   = midtones_curr
        self.highlight_curr  = highlight_curr
        self.update()
     

    def set_equalisation(self, value):
        self.equalisation_curr = value
        self.update()  

    def update(self):
        x = self.image_orig_small.copy()
        self.image_curr = self._update(x)
       
        self.update_histogram()


    def split_preview_toogle(self):
        self.update()   

        height = self.image_curr.shape[1]
        width  = self.image_curr.shape[1]

        if self.split_preview != 0:
            self.image_curr[:, 0:width//2, :] = self.image_orig_small[:, 0:width//2, :]

            self.image_curr = cv2.line(self.image_curr, (width//2, 0), (width//2, height), (0.0, 0.7, 0), 2) 

            self.split_preview = 0
        else:
            self.split_preview = 1



    def export(self, file_name, extension):
        print("exporting to ", file_name)
        x = self.image_orig.copy()
        result = self._update(x)

        result = numpy.array(result*255, dtype=numpy.uint8)
        if extension == "jpg":
            cv2.imwrite(file_name + ".jpg", result, [int(cv2.IMWRITE_JPEG_QUALITY), 99])
        else:
            cv2.imwrite(file_name + ".png", result)


    def _update(self, x):
        x = filters.adjust_ev(x, self.ev_curr)
        x = filters.adjust_white_balance(x, self.temperature_curr)
        
        x = filters.global_brightness(x, self.brightness_curr)
        x = filters.global_contrast(x, self.contrast_curr)
        x = filters.global_saturation(x, self.saturation_curr)
        x = filters.local_saturation(x, self.vibrance_curr)

        x = numpy.clip(x, 0.0, 1.0)

        x = filters.adjust_tones(x, self.shadows_curr, self.midtones_curr, self.highlight_curr)
        x = numpy.clip(x, 0.0, 1.0)

        x = filters.histogram_equalisation(x, self.equalisation_curr)
        x = numpy.clip(x, 0.0, 1.0)

        return x

    def update_histogram(self): 
        #tmp = cv2.resize(self.image_curr, (self.image_curr.shape[1]//16, self.image_curr.shape[0]//16))   
        tmp = numpy.array(self.image_curr*255, dtype=numpy.uint8)

        hist_size = 255

        self.histogram = numpy.zeros((4, hist_size))


        r = cv2.calcHist([tmp], [0], None, [hist_size], [0, 256])[:, 0]
        g = cv2.calcHist([tmp], [1], None, [hist_size], [0, 256])[:, 0]
        b = cv2.calcHist([tmp], [2], None, [hist_size], [0, 256])[:, 0]


        w = r + g + b
        w = w/(w.sum() + 1e-6)
            
        self.histogram[0] = w   
        self.histogram[1] = r/(r.sum() + 1e-6)
        self.histogram[2] = g/(g.sum() + 1e-6)
        self.histogram[3] = b/(b.sum() + 1e-6)

        # histogram smoothing
        window_size = 7
        kernel = numpy.ones(window_size) / window_size

        for n in range(self.histogram.shape[0]):
            self.histogram[n] = numpy.convolve(self.histogram[n], kernel, mode='same')
    
        return self.histogram



    def save(self, file_name):
        print("saving to ", file_name)
        result = {}

        result["ev"] = {}
        result["ev"]["default"] = self.ev_default
        result["ev"]["min"]     = self.ev_min
        result["ev"]["max"]     = self.ev_max
        result["ev"]["curr"]    = self.ev_curr

        result["temperature"] = {}
        result["temperature"]["default"] = self.temperature_default
        result["temperature"]["min"]     = self.temperature_min
        result["temperature"]["max"]     = self.temperature_max
        result["temperature"]["curr"]    = self.temperature_curr

        result["brightness"] = {}
        result["brightness"]["default"] = self.brightness_default
        result["brightness"]["min"]     = self.brightness_min
        result["brightness"]["max"]     = self.brightness_max
        result["brightness"]["curr"]    = self.brightness_curr

        result["contrast"] = {}
        result["contrast"]["default"] = self.contrast_default
        result["contrast"]["min"]     = self.contrast_min
        result["contrast"]["max"]     = self.contrast_max
        result["contrast"]["curr"]    = self.contrast_curr

        result["saturation"] = {}
        result["saturation"]["default"] = self.saturation_default
        result["saturation"]["min"]     = self.saturation_min
        result["saturation"]["max"]     = self.saturation_max
        result["saturation"]["curr"]    = self.saturation_curr

        result["vibrance"] = {}
        result["vibrance"]["default"] = self.vibrance_default
        result["vibrance"]["min"]     = self.vibrance_min
        result["vibrance"]["max"]     = self.vibrance_max
        result["vibrance"]["curr"]    = self.vibrance_curr


        result["tones"] = {}
        result["tones"]["default"]         = self.tones_default
        result["tones"]["min"]             = self.tones_min
        result["tones"]["max"]             = self.tones_max
        result["tones"]["shadows_curr"]    = self.shadows_curr
        result["tones"]["midtones_curr"]   = self.midtones_curr
        result["tones"]["highlight_curr"]  = self.highlight_curr


        result["equalisation"] = {}
        result["equalisation"]["default"] = self.equalisation_default
        result["equalisation"]["min"]     = self.equalisation_min
        result["equalisation"]["max"]     = self.equalisation_max
        result["equalisation"]["curr"]    = self.equalisation_curr

        result_json = json.dumps(result)
                                 
        f = open(file_name, 'w')
        f.write(result_json)

    def load(self, file_name):
        print("loading from ", file_name)
        if os.path.exists(file_name):
            f = open(file_name)
            result = json.load(f)

            self.ev_default = float(result["ev"]["default"])
            self.ev_min     = float(result["ev"]["min"])
            self.ev_max     = float(result["ev"]["max"])
            self.ev_curr    = float(result["ev"]["curr"])

            self.temperature_default = float(result["temperature"]["default"])
            self.temperature_min     = float(result["temperature"]["min"])
            self.temperature_max     = float(result["temperature"]["max"])
            self.temperature_curr    = float(result["temperature"]["curr"])

            self.brightness_default = float(result["brightness"]["default"])
            self.brightness_min     = float(result["brightness"]["min"])
            self.brightness_max     = float(result["brightness"]["max"])
            self.brightness_curr    = float(result["brightness"]["curr"])
            
            self.contrast_default = float(result["contrast"]["default"])
            self.contrast_min     = float(result["contrast"]["min"])
            self.contrast_max     = float(result["contrast"]["max"])
            self.contrast_curr    = float(result["contrast"]["curr"])

            self.saturation_default = float(result["saturation"]["default"])
            self.saturation_min     = float(result["saturation"]["min"])
            self.saturation_max     = float(result["saturation"]["max"])
            self.saturation_curr    = float(result["saturation"]["curr"])

            self.vibrance_default = float(result["vibrance"]["default"])
            self.vibrance_min     = float(result["vibrance"]["min"])
            self.vibrance_max     = float(result["vibrance"]["max"])
            self.vibrance_curr    = float(result["vibrance"]["curr"])
            
            
            self.tones_default      = float(result["tones"]["default"])
            self.tones_min          = float(result["tones"]["min"])             
            self.tones_max          = float(result["tones"]["max"])             
            self.shadows_curr       = float(result["tones"]["shadows_curr"])
            self.midtones_curr      = float(result["tones"]["midtones_curr"])
            self.highlight_curr     = float(result["tones"]["highlight_curr"])

            self.equalisation_default = float(result["equalisation"]["default"])
            self.equalisation_min     = float(result["equalisation"]["min"])
            self.equalisation_max     = float(result["equalisation"]["max"])
            self.equalisation_curr    = float(result["equalisation"]["curr"])
        