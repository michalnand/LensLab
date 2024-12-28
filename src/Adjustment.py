import numpy

import Filters
from ImageSettings import *


class Adjustment(ImageSettings):

    def __init__(self):
        super().__init__()
        self.default_adjustment()
    
    def get_count(self):
        return 16   



    def default_adjustment(self):
        self.ev_curr            = self.ev_default
        self.wb_curr            = self.wb_default

        self.brightness_curr    = self.brightness_default
        self.contrast_curr      = self.contrast_default

        self.saturation_curr    = self.saturation_default
        self.vibrance_curr      = self.vibrance_default

        self.tones_dark_curr    = self.tones_default
        self.tones_mid_curr     = self.tones_default
        self.tones_high_curr    = self.tones_default

        self.colors_red_curr    = self.colors_default
        self.colors_green_curr  = self.colors_default
        self.colors_blue_curr   = self.colors_default

        self.equalisation_curr  = self.equalisation_default
        
        self.blur_curr          = self.blur_default
        self.sharpen_curr       = self.sharpen_default

        self.bilateral_curr     = self.bilateral_default


    def random_adjustment(self, p = 0.1):
        self.default_adjustment()

        if numpy.random.rand() < p:
            self.ev_curr            = numpy.random.uniform(self.ev_min, self.ev_max)

        if numpy.random.rand() < p:
            self.wb_curr            = numpy.random.uniform(self.wb_min, self.wb_max)

        if numpy.random.rand() < p:
            self.brightness_curr    = numpy.random.uniform(self.brightness_min, self.brightness_max)

        if numpy.random.rand() < p:
            self.contrast_curr      = numpy.random.uniform(self.contrast_min, self.contrast_max)
        
        if numpy.random.rand() < p:
            self.saturation_curr    = numpy.random.uniform(self.saturation_min, self.saturation_max)
        
        if numpy.random.rand() < p:
            self.vibrance_curr      = numpy.random.uniform(self.vibrance_min, self.vibrance_max)
        
        if numpy.random.rand() < p:
            self.tones_dark_curr    = numpy.random.uniform(self.tones_min, self.tones_max)
        
        if numpy.random.rand() < p:
            self.tones_mid_curr     = numpy.random.uniform(self.tones_min, self.tones_max)
        
        if numpy.random.rand() < p:
            self.tones_high_curr    = numpy.random.uniform(self.tones_min, self.tones_max)

        if numpy.random.rand() < p:
            self.colors_red_curr    = numpy.random.uniform(self.colors_min, self.colors_max)
        
        if numpy.random.rand() < p:
            self.colors_green_curr  = numpy.random.uniform(self.colors_min, self.colors_max)

        if numpy.random.rand() < p:
            self.colors_blue_curr   = numpy.random.uniform(self.colors_min, self.colors_max)
        
        if numpy.random.rand() < p:
            self.equalisation_curr  = numpy.random.uniform(self.equalisation_min, self.equalisation_max)

        if numpy.random.rand() < p:
            self.blur_curr          = numpy.random.uniform(self.blur_min, self.blur_max)

        if numpy.random.rand() < p:
            self.sharpen_curr       = numpy.random.uniform(self.sharpen_min, self.sharpen_max)

        if numpy.random.rand() < p:
            self.bilateral_curr     = numpy.random.uniform(self.bilateral_min, self.bilateral_max)


    def set_dadjustment(self, dadjustment):

        dadjustment  = numpy.clip(dadjustment, -1.0, 1.0).astype(numpy.float32)

        dv                      = dadjustment[0]*(self.ev_max - self.ev_min)
        self.ev_curr            = numpy.clip(self.ev_curr + dv, self.ev_min, self.ev_max)

        dv                      = dadjustment[1]*(self.wb_max - self.wb_min)
        self.wb_curr            = numpy.clip(self.wb_curr + dv, self.wb_min, self.wb_max)

        dv                      = dadjustment[2]*(self.brightness_max - self.brightness_min)
        self.brightness_curr    = numpy.clip(self.brightness_curr + dv, self.brightness_min, self.brightness_max)

        dv                      = dadjustment[3]*(self.contrast_max - self.contrast_min)
        self.contrast_curr      = numpy.clip(self.contrast_curr + dv, self.contrast_min, self.contrast_max)

        dv                      = dadjustment[4]*(self.saturation_max - self.saturation_min)
        self.saturation_curr    = numpy.clip(self.saturation_curr + dv, self.saturation_min, self.saturation_max)

        dv                      = dadjustment[5]*(self.vibrance_max - self.vibrance_min)
        self.vibrance_curr      = numpy.clip(self.vibrance_curr + dv, self.vibrance_min, self.vibrance_max)

        dv                      = dadjustment[6]*(self.tones_max - self.tones_min)
        self.tones_dark_curr    = numpy.clip(self.tones_dark_curr + dv, self.tones_min, self.tones_max)

        dv                      = dadjustment[7]*(self.tones_max - self.tones_min)
        self.tones_mid_curr     = numpy.clip(self.tones_mid_curr + dv, self.tones_min, self.tones_max)

        dv                      = dadjustment[8]*(self.tones_max - self.tones_min)
        self.tones_high_curr    = numpy.clip(self.tones_high_curr + dv, self.tones_min, self.tones_max)


        dv                      = dadjustment[9]*(self.colors_max - self.colors_min)
        self.colors_red_curr    = numpy.clip(self.colors_red_curr + dv, self.colors_min, self.colors_max)

        dv                      = dadjustment[10]*(self.colors_max - self.colors_min)
        self.colors_green_curr  = numpy.clip(self.colors_green_curr + dv, self.colors_min, self.colors_max)

        dv                      = dadjustment[11]*(self.colors_max - self.colors_min)
        self.colors_blue_curr   = numpy.clip(self.colors_blue_curr + dv, self.colors_min, self.colors_max)
        

        dv                      = dadjustment[12]*(self.equalisation_max - self.equalisation_min)
        self.equalisation_curr  = numpy.clip(self.equalisation_curr + dv, self.equalisation_min, self.equalisation_max)

        dv                      = dadjustment[13]*(self.blur_max - self.blur_min)
        self.blur_curr          = numpy.clip(self.blur_curr + dv, self.blur_min, self.blur_max)

        dv                      = dadjustment[14]*(self.sharpen_max - self.sharpen_min)
        self.sharpen_curr       = numpy.clip(self.sharpen_curr + dv, self.sharpen_min, self.sharpen_max)

        dv                      = dadjustment[15]*(self.bilateral_max - self.bilateral_min)
        self.bilateral_curr     = numpy.clip(self.bilateral_curr + dv, self.bilateral_min, self.bilateral_max)
        



    def apply_adjustment(self, image):
        x = image.copy()

        if self.ev_curr != self.ev_default:
            x = Filters.adjust_ev(x, self.ev_curr)

        if self.wb_curr != self.wb_default:
            x = Filters.adjust_white_balance(x, self.wb_curr)
        
        if self.brightness_curr != self.brightness_default:
            x = Filters.global_brightness(x, self.brightness_curr)
        
        if self.contrast_curr != self.contrast_default:
            x = Filters.global_contrast(x, self.contrast_curr)

        if self.saturation_curr != self.saturation_default:
            x = Filters.global_saturation(x, self.saturation_curr)

        if self.vibrance_curr != self.vibrance_default:
            x = Filters.local_saturation(x, self.vibrance_curr)

        x = numpy.clip(x, 0.0, 1.0)

        x = Filters.adjust_tones(x, self.tones_dark_curr, self.tones_mid_curr, self.tones_high_curr)
        x = numpy.clip(x, 0.0, 1.0)

        if self.colors_red_curr != self.colors_default or self.colors_green_curr != self.colors_default or self.colors_blue_curr != self.colors_default:
            x = Filters.adjust_colors(x, self.colors_red_curr, self.colors_green_curr, self.colors_blue_curr)

        x = Filters.histogram_equalisation(x, self.equalisation_curr)
        x = numpy.clip(x, 0.0, 1.0)

        if self.blur_curr != self.blur_default:
            x = Filters.blur_filter(x, self.blur_curr)

        if self.sharpen_curr != self.sharpen_default:
            x = Filters.sharpen_filter(x, self.sharpen_curr)
        
        if self.bilateral_curr != self.bilateral_default:
            x = Filters.bilateral_filter(x, self.bilateral_curr)

        return x

