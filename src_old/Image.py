import numpy
import cv2
import json
import os

import filters

class Image:

    def __init__(self, image_full):
        self.image_orig = image_full.copy()

        self.scale_ratio = 4

        self.image_orig_small   = cv2.resize(self.image_orig, (self.image_orig.shape[1]//self.scale_ratio, self.image_orig.shape[0]//self.scale_ratio))
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


        self.blur_default     = 0.0
        self.blur_min         = 0.0
        self.blur_max         = 1.0
        self.blur_curr        = 0.0

        self.sharpen_default     = 0.0
        self.sharpen_min         = 0.0
        self.sharpen_max         = 1.0
        self.sharpen_curr        = 0.0

        self.bilateral_default     = 0.0
        self.bilateral_min         = 0.0
        self.bilateral_max         = 1.0
        self.bilateral_curr        = 0.0

        self.split_preview = 0

   
        self.crop_modes     = ["Original image", "Free hand", "16:9", "4:3", "3:2", "1:1", "9:16", "3:4", "2:3", "1.85:1", "2.35:1", "16:10"]
        self.crop_ratio_x   = [-1,   -1, 16, 4, 3, 1,  9, 3, 2, 1.85, 2.35, 16]
        self.crop_ratio_y   = [-1,   -1,  9, 3, 2, 1, 16, 4, 3,    1,    1, 10]

        self.crop_default   = 0
        self.crop_curr      = 0

       
        self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = self._get_crop_rectangle(self.image_orig_small.shape[1], self.image_orig_small.shape[0])


        self.crop_x = (self.crop_right  - self.crop_left)//2
        self.crop_y = (self.crop_bottom - self.crop_top)//2

    def set_image(self, img):
        self.image_orig = img.copy()
        self.image_orig_small   = cv2.resize(self.image_orig, (self.image_orig.shape[1]//self.scale_ratio, self.image_orig.shape[0]//self.scale_ratio))
        self.image_curr         = self.image_orig_small.copy()

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
    
    def get_blur(self):
        return self.blur_min, self.blur_max, self.blur_curr 
    
    def get_sharpen(self):
        return self.sharpen_min, self.sharpen_max, self.sharpen_curr 
    
    def get_bilateral(self):
        return self.bilateral_min, self.bilateral_max, self.bilateral_curr 
    

    
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

    def set_blur(self, value):
        self.blur_curr = value
        self.update()  

    def set_sharpen(self, value):
        self.sharpen_curr = value
        self.update()  

    def set_bilateral(self, value):
        self.bilateral_curr = value
        self.update()  


    def set_crop_aspect_ratio(self, mode_name):
        self.crop_curr = self.crop_default

        for i in range(len(self.crop_modes)):
            if mode_name == self.crop_modes[i]:
                self.crop_curr = i
                break

        self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = self._get_crop_rectangle(self.image_orig_small.shape[1], self.image_orig_small.shape[0])
        self.crop_x = (self.crop_right  - self.crop_left)//2
        self.crop_y = (self.crop_bottom - self.crop_top)//2

        self.image_curr = self._plot_crop_rectangle(self.image_processed.copy())
       

    def _plot_crop_rectangle(self, img):    
        result = cv2.line(img, (self.crop_left, self.crop_top), (self.crop_right, self.crop_top), (0.8, 0.8, 0.8), 2)
        result = cv2.line(result, (self.crop_left, self.crop_bottom), (self.crop_right, self.crop_bottom), (0.8, 0.8, 0.8), 2)
        result = cv2.line(result, (self.crop_left, self.crop_top), (self.crop_left, self.crop_bottom), (0.8, 0.8, 0.8), 2)
        result = cv2.line(result, (self.crop_right, self.crop_top), (self.crop_right, self.crop_bottom), (0.8, 0.8, 0.8), 2)

        result[self.crop_top:self.crop_bottom, self.crop_left:self.crop_right, :]*= 5.0
        result/= 5.0

        return result



    def _get_crop_rectangle(self, width, height, center_x = None, center_y = None):
        aspect_width = self.crop_ratio_x[self.crop_curr]
        aspect_height = self.crop_ratio_y[self.crop_curr]

        # original image
        if aspect_width < 0 or aspect_height < 0:
            rect_left      = 0
            rect_right     = width
            rect_top       = 0
            rect_bottom    = height
        # free hand mode
        elif aspect_width < 0 or aspect_height < 0:
            rect_left      = 0
            rect_right     = width
            rect_top       = 0
            rect_bottom    = height

        else:
            # Calculate the aspect ratio
            aspect_ratio = aspect_width / aspect_height

            # Calculate the aspect ratio of the original rectangle
            original_aspect_ratio = width / height

            if original_aspect_ratio > aspect_ratio:
                # Original is wider than the desired aspect ratio
                rect_height = height
                rect_width = rect_height * aspect_ratio
            else:
                # Original is taller than the desired aspect ratio
                rect_width = width
                rect_height = rect_width / aspect_ratio

            if center_x is None:
                center_x = width/2

            if center_y is None:
                center_y = height/2

            # Ensure the center is within bounds and adjust if needed
            half_rect_width = rect_width / 2
            half_rect_height = rect_height / 2

            clipped_center_x = numpy.clip(center_x, half_rect_width, width - half_rect_width)
            clipped_center_y = numpy.clip(center_y, half_rect_height, height - half_rect_height)

            # Calculate the coordinates of the rectangle
            rect_left = clipped_center_x - half_rect_width
            rect_right = clipped_center_x + half_rect_width
            rect_top = clipped_center_y - half_rect_height
            rect_bottom = clipped_center_y + half_rect_height



        rect_right   = int(numpy.clip(rect_right, 0, width-1))
        rect_left    = int(numpy.clip(rect_left,  0, width-1))

        rect_bottom  = int(numpy.clip(rect_bottom, 0, height-1))
        rect_top     = int(numpy.clip(rect_top,    0, height-1))

        return rect_left, rect_right, rect_top, rect_bottom



    def set_crop_event(self, x, y, mouse_click):
        center_x = self.image_curr.shape[1]*x 
        center_y = self.image_curr.shape[0]*y

        self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = self._get_crop_rectangle(self.image_orig_small.shape[1], self.image_orig_small.shape[0], center_x, center_y)

        self.crop_x = (self.crop_right  - self.crop_left)//2
        self.crop_y = (self.crop_bottom - self.crop_top)//2

        self.image_curr = self._plot_crop_rectangle(self.image_processed.copy())
       

    def update(self):
        self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = self._get_crop_rectangle(self.image_orig_small.shape[1], self.image_orig_small.shape[0], self.crop_x, self.crop_y)

        
        x = self.image_orig_small.copy()
        self.image_processed = self._update(x)
        self.image_curr      = self._plot_crop_rectangle(self.image_processed.copy())

       
        self.update_histogram()

        if self.split_preview:
            height = self.image_curr.shape[1]
            width  = self.image_curr.shape[1] 

            self.image_curr[:, 0:width//2, :] = self.image_orig_small[:, 0:width//2, :]
            self.image_curr = cv2.line(self.image_curr, (width//2, 0), (width//2, height), (0.0, 0.7, 0), 2) 


    def split_preview_toogle(self):   
        if self.split_preview != 0:
            self.split_preview = 0
        else:
            self.split_preview = 1

        self.update()


    def process_full_resolution(self, x):
        result = self._update(x.copy())

        crop_left   = int(numpy.clip(self.crop_left*self.scale_ratio, 0, x.shape[1]))
        crop_right  = int(numpy.clip(self.crop_right*self.scale_ratio, 0, x.shape[1]))
        crop_top    = int(numpy.clip(self.crop_top*self.scale_ratio, 0, x.shape[0]))
        crop_bottom = int(numpy.clip(self.crop_bottom*self.scale_ratio, 0, x.shape[0]))

        result = result[crop_top:crop_bottom, crop_left:crop_right, :]

        return result

    def export(self, file_name, extension, quality = 99):
        print("exporting to ", file_name)
        
        result = self.process_full_resolution(self.image_orig)

        result = numpy.array(result*255, dtype=numpy.uint8)
        if extension == "jpg":
            cv2.imwrite(file_name + ".jpg", result, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        else:
            cv2.imwrite(file_name + ".png", result)


    def _update(self, x):
        if self.ev_curr != self.ev_default:
            x = filters.adjust_ev(x, self.ev_curr)

        if self.temperature_curr != self.temperature_default:
            x = filters.adjust_white_balance(x, self.temperature_curr)
        
        if self.brightness_curr != self.brightness_default:
            x = filters.global_brightness(x, self.brightness_curr)
        
        if self.contrast_curr != self.contrast_default:
            x = filters.global_contrast(x, self.contrast_curr)

        if self.saturation_curr != self.saturation_default:
            x = filters.global_saturation(x, self.saturation_curr)

        if self.vibrance_curr != self.vibrance_default:
            x = filters.local_saturation(x, self.vibrance_curr)

        x = numpy.clip(x, 0.0, 1.0)

        x = filters.adjust_tones(x, self.shadows_curr, self.midtones_curr, self.highlight_curr)
        x = numpy.clip(x, 0.0, 1.0)

        x = filters.histogram_equalisation(x, self.equalisation_curr)
        x = numpy.clip(x, 0.0, 1.0)

        if self.blur_curr != self.blur_default:
            x = filters.blur_filter(x, self.blur_curr)

        if self.sharpen_curr != self.sharpen_default:
            x = filters.sharpen_filter(x, self.sharpen_curr)
        
        if self.bilateral_curr != self.bilateral_default:
            x = filters.bilateral_filter(x, self.bilateral_curr)

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
        window_size = 9
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


        result["blur"] = {}
        result["blur"]["default"] = self.blur_default
        result["blur"]["min"]     = self.blur_min
        result["blur"]["max"]     = self.blur_max
        result["blur"]["curr"]    = self.blur_curr

        result["sharpen"] = {}
        result["sharpen"]["default"] = self.sharpen_default
        result["sharpen"]["min"]     = self.sharpen_min
        result["sharpen"]["max"]     = self.sharpen_max
        result["sharpen"]["curr"]    = self.sharpen_curr

        result["bilateral"] = {}
        result["bilateral"]["default"] = self.bilateral_default
        result["bilateral"]["min"]     = self.bilateral_min
        result["bilateral"]["max"]     = self.bilateral_max
        result["bilateral"]["curr"]    = self.bilateral_curr

        result["crop"] = {}
        result["crop"]["default"]   = self.crop_default
        result["crop"]["curr"]      = self.crop_curr
        result["crop"]["left"]      = self.crop_left
        result["crop"]["right"]     = self.crop_right
        result["crop"]["top"]       = self.crop_top
        result["crop"]["bottom"]    = self.crop_bottom
        result["crop"]["x"]         = self.crop_x
        result["crop"]["y"]         = self.crop_y
        
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


            self.blur_default   = float(result["blur"]["default"])
            self.blur_min       = float(result["blur"]["min"])
            self.blur_max       = float(result["blur"]["max"])
            self.blur_curr      = float(result["blur"]["curr"])

            self.sharpen_default = float(result["sharpen"]["default"])
            self.sharpen_min     = float(result["sharpen"]["min"])
            self.sharpen_max     = float(result["sharpen"]["max"])
            self.sharpen_curr    = float(result["sharpen"]["curr"])

            self.bilateral_default = float(result["bilateral"]["default"])
            self.bilateral_min     = float(result["bilateral"]["min"])
            self.bilateral_max     = float(result["bilateral"]["max"])
            self.bilateral_curr    = float(result["bilateral"]["curr"])


            self.crop_default   = int(result["crop"]["default"])
            self.crop_curr      = int(result["crop"]["curr"])

            self.crop_left      = int(result["crop"]["left"])
            self.crop_right     = int(result["crop"]["right"])
            self.crop_top       = int(result["crop"]["top"])
            self.crop_bottom    = int(result["crop"]["bottom"])

            self.crop_x         = int(result["crop"]["x"])      
            self.crop_y         = int(result["crop"]["y"])     


