import json
import os

class ImageSettings:

    def __init__(self):
        self.set_default()

    def set_default(self):
        self.ev_min     = -4.0
        self.ev_max     = 4.0
        self.ev_default = 0.0
        self.ev_curr    = self.ev_default

        self.ev_adaptive_min     = -1.0
        self.ev_adaptive_max     = 1.0
        self.ev_adaptive_default = 0.0
        self.ev_adaptive_curr    = self.ev_adaptive_default
        

        self.wb_min     = 2000.0
        self.wb_max     = 20000.0
        self.wb_default = 6500.0
        self.wb_curr    = self.wb_default


        self.brightness_min     = -1.0
        self.brightness_max     = 1.0
        self.brightness_default = 0.0
        self.brightness_curr    = self.brightness_default

        
        self.contrast_min       = 0.0
        self.contrast_max       = 5.0
        self.contrast_default   = 1.0
        self.contrast_curr      = self.contrast_default


        self.clarity_min        = 0.0
        self.clarity_max        = 2.0
        self.clarity_default    = 0.0
        self.clarity_curr       = self.clarity_default
     

        self.saturation_min       = 0.0
        self.saturation_max       = 4.0
        self.saturation_default   = 1.0
        self.saturation_curr      = self.saturation_default

        self.vibrance_min       = 0.0
        self.vibrance_max       = 4.0
        self.vibrance_default   = 1.0
        self.vibrance_curr      = self.vibrance_default

        self.equalisation_min       = 0.0   
        self.equalisation_max       = 1.0
        self.equalisation_default   = 0.0
        self.equalisation_curr      = self.equalisation_default


        self.blur_min         = 0.0
        self.blur_max         = 1.0
        self.blur_default     = 0.0
        self.blur_curr        = self.blur_default


        
        self.tones_min          = -0.1
        self.tones_max          = 0.1
        self.tones_default      = 0.0
        self.tones_dark_curr    = self.tones_default
        self.tones_mid_curr     = self.tones_default
        self.tones_high_curr    = self.tones_default


        self.colors_min         = -1.0
        self.colors_max         = 1.0 
        self.colors_default     = 0.0
        self.colors_red_curr    = self.colors_default
        self.colors_green_curr  = self.colors_default 
        self.colors_blue_curr   = self.colors_default



        self.sharpen_min         = 0.0
        self.sharpen_max         = 1.0
        self.sharpen_default     = 0.0
        self.sharpen_curr        = self.sharpen_default
            
        
        self.bilateral_min         = 0.0
        self.bilateral_max         = 1.0
        self.bilateral_default     = 0.0
        self.bilateral_curr        = self.bilateral_default


        self.crop_modes     = ["Original image", "Free hand", "16:9", "4:3", "3:2", "1:1", "9:16", "3:4", "2:3", "1.85:1", "2.35:1", "16:10"]
        self.crop_ratio_x   = [-1,   -1, 16, 4, 3, 1,  9, 3, 2, 1.85, 2.35, 16]
        self.crop_ratio_y   = [-1,   -1,  9, 3, 2, 1, 16, 4, 3,    1,    1, 10]

        self.crop_default   = 0
        self.crop_curr      = 0


        self.crop_x         = 0.5
        self.crop_y         = 0.5


        self.stacking_modes = ["mean", "max", "min", "median", "bracketing"]



    def save_settings(self, file_name):
        print("saving settings to ", file_name)
        result = {}

        result["ev"] = {}
        result["ev"]["min"]     = self.ev_min
        result["ev"]["max"]     = self.ev_max
        result["ev"]["default"] = self.ev_default
        result["ev"]["curr"]    = self.ev_curr


        result["ev_adaptive"] = {}
        result["ev_adaptive"]["min"]     = self.ev_adaptive_min
        result["ev_adaptive"]["max"]     = self.ev_adaptive_max
        result["ev_adaptive"]["default"] = self.ev_adaptive_default
        result["ev_adaptive"]["curr"]    = self.ev_adaptive_curr


        result["wb"] = {}
        result["wb"]["min"]     = self.wb_min
        result["wb"]["max"]     = self.wb_max
        result["wb"]["default"] = self.wb_default
        result["wb"]["curr"]    = self.wb_curr

        result["brightness"] = {}
        result["brightness"]["min"]     = self.brightness_min
        result["brightness"]["max"]     = self.brightness_max
        result["brightness"]["default"] = self.brightness_default
        result["brightness"]["curr"]    = self.brightness_curr

        result["contrast"] = {}
        result["contrast"]["min"]       = self.contrast_min
        result["contrast"]["max"]       = self.contrast_max
        result["contrast"]["default"]   = self.contrast_default
        result["contrast"]["curr"]      = self.contrast_curr

        result["clarity"] = {}
        result["clarity"]["min"]        = self.clarity_min
        result["clarity"]["max"]        = self.clarity_max
        result["clarity"]["default"]    = self.clarity_default
        result["clarity"]["curr"]       = self.clarity_curr
               
        result["saturation"] = {}
        result["saturation"]["min"]     = self.saturation_min
        result["saturation"]["max"]     = self.saturation_max
        result["saturation"]["default"] = self.saturation_default
        result["saturation"]["curr"]    = self.saturation_curr

        result["vibrance"] = {}
        result["vibrance"]["min"]     = self.vibrance_min
        result["vibrance"]["max"]     = self.vibrance_max
        result["vibrance"]["default"] = self.vibrance_default
        result["vibrance"]["curr"]    = self.vibrance_curr


        result["tones"] = {}
        result["tones"]["min"]             = self.tones_min
        result["tones"]["max"]             = self.tones_max
        result["tones"]["default"]         = self.tones_default
        result["tones"]["tones_dark_curr"] = self.tones_dark_curr
        result["tones"]["tones_mid_curr"]  = self.tones_mid_curr
        result["tones"]["tones_high_curr"] = self.tones_high_curr
    
        result["colors"] = {}
        result["colors"]["min"]         = self.colors_min
        result["colors"]["max"]         = self.colors_max
        result["colors"]["default"]     = self.colors_default
        result["colors"]["red"]         = self.colors_red_curr
        result["colors"]["green"]       = self.colors_green_curr
        result["colors"]["blue"]        = self.colors_blue_curr


        result["equalisation"] = {}
        result["equalisation"]["min"]     = self.equalisation_min
        result["equalisation"]["max"]     = self.equalisation_max
        result["equalisation"]["default"] = self.equalisation_default
        result["equalisation"]["curr"]    = self.equalisation_curr


        result["blur"] = {}
        result["blur"]["min"]     = self.blur_min
        result["blur"]["max"]     = self.blur_max
        result["blur"]["default"] = self.blur_default
        result["blur"]["curr"]    = self.blur_curr

        result["sharpen"] = {}
        result["sharpen"]["min"]     = self.sharpen_min
        result["sharpen"]["max"]     = self.sharpen_max
        result["sharpen"]["default"] = self.sharpen_default
        result["sharpen"]["curr"]    = self.sharpen_curr

        result["bilateral"] = {}
        result["bilateral"]["min"]     = self.bilateral_min
        result["bilateral"]["max"]     = self.bilateral_max
        result["bilateral"]["default"] = self.bilateral_default
        result["bilateral"]["curr"]    = self.bilateral_curr

        result["crop"] = {}
        
        result["crop"]["crop_modes"]    = self.crop_modes
        result["crop"]["crop_ratio_x"]  = self.crop_ratio_x
        result["crop"]["crop_ratio_y"]  = self.crop_ratio_y
        result["crop"]["default"]       = self.crop_default
        result["crop"]["curr"]          = self.crop_curr


        result["crop"]["x"]     = self.crop_x
        result["crop"]["y"]     = self.crop_y
        
        
        result_json = json.dumps(result)
                                 
        f = open(file_name, 'w')
        f.write(result_json)



    def load_settings(self, file_name):
        print("loading settings from ", file_name)
        if os.path.exists(file_name):
            f = open(file_name)
            result = json.load(f)

            if "ev" in result:
                self.ev_min     = result["ev"]["min"]
                self.ev_max     = result["ev"]["max"]
                self.ev_default = result["ev"]["default"]
                self.ev_curr    = result["ev"]["curr"]

            if "ev_adaptive" in result:
                self.ev_adaptive_min     = result["ev_adaptive"]["min"]
                self.ev_adaptive_max     = result["ev_adaptive"]["max"]
                self.ev_adaptive_default = result["ev_adaptive"]["default"]
                self.ev_adaptive_curr    = result["ev_adaptive"]["curr"]

            if "wb" in result:
                self.wb_min     = result["wb"]["min"]
                self.wb_max     = result["wb"]["max"]
                self.wb_default = result["wb"]["default"]
                self.wb_curr    = result["wb"]["curr"]

            if "brightness" in result:
                self.brightness_min     = result["brightness"]["min"]
                self.brightness_max     = result["brightness"]["max"]
                self.brightness_default = result["brightness"]["default"]
                self.brightness_curr    = result["brightness"]["curr"]

            if "contrast" in result:
                self.contrast_min       = result["contrast"]["min"]
                self.contrast_max       = result["contrast"]["max"]
                self.contrast_default   = result["contrast"]["default"]
                self.contrast_curr      = result["contrast"]["curr"]

            if "clarity" in result:
                self.clarity_min     = result["clarity"]["min"]
                self.clarity_max     = result["clarity"]["max"]
                self.clarity_default = result["clarity"]["default"]
                self.clarity_curr    = result["clarity"]["curr"]

            if "saturation" in result:
                self.saturation_min     = result["saturation"]["min"]
                self.saturation_max     = result["saturation"]["max"]
                self.saturation_default = result["saturation"]["default"]
                self.saturation_curr    = result["saturation"]["curr"]

            if "vibrance" in result:
                self.vibrance_min       = result["vibrance"]["min"]
                self.vibrance_max       = result["vibrance"]["max"]
                self.vibrance_default   = result["vibrance"]["default"]
                self.vibrance_curr      = result["vibrance"]["curr"]

            if "tones" in result:
                self.tones_min          = result["tones"]["min"]
                self.tones_max          = result["tones"]["max"]
                self.tones_default      = result["tones"]["default"]
                self.tones_dark_curr    = result["tones"]["tones_dark_curr"]
                self.tones_mid_curr     = result["tones"]["tones_mid_curr"]
                self.tones_high_curr    = result["tones"]["tones_high_curr"]

            if "colors" in result:
                self.colors_min             = result["colors"]["min"]
                self.colors_max             = result["colors"]["max"]
                self.colors_default         = result["colors"]["default"]
                self.colors_red_curr        = result["colors"]["red"]
                self.colors_green_curr      = result["colors"]["green"]
                self.colors_blue_curr       = result["colors"]["blue"]

            if "equalisation" in result:
                self.equalisation_min       = result["equalisation"]["min"]
                self.equalisation_max       = result["equalisation"]["max"]
                self.equalisation_default   = result["equalisation"]["default"]
                self.equalisation_curr      = result["equalisation"]["curr"]

            if "blur" in result:
                self.blur_min       =   result["blur"]["min"]
                self.blur_max       =   result["blur"]["max"]
                self.blur_default   =   result["blur"]["default"]
                self.blur_curr      =   result["blur"]["curr"]

            if "sharpen" in result:
                self.sharpen_min    = result["sharpen"]["min"]
                self.sharpen_max    = result["sharpen"]["max"]
                self.sharpen_default= result["sharpen"]["default"]
                self.sharpen_curr   = result["sharpen"]["curr"]

            if "bilateral" in result:
                self.bilateral_min      = result["bilateral"]["min"]
                self.bilateral_max      = result["bilateral"]["max"]
                self.bilateral_default  = result["bilateral"]["default"]
                self.bilateral_curr     = result["bilateral"]["curr"]

            if "crop" in result:
                self.crop_modes     = result["crop"]["crop_modes"]
                self.crop_ratio_x   = result["crop"]["crop_ratio_x"]
                self.crop_ratio_y   = result["crop"]["crop_ratio_y"]
                self.crop_default   = result["crop"]["default"]
                self.crop_curr      = result["crop"]["curr"]


                self.crop_x         = result["crop"]["x"]
                self.crop_y         = result["crop"]["y"]
            

        else:
            print("setting file not found")


    def get_ev_state(self):
        return self.ev_min, self.ev_max, self.ev_default, self.ev_curr

    def set_ev(self, value):
        self.ev_curr = value
        self.settings_changed_callback()

    
    def get_ev_adaptive_state(self):
        return self.ev_adaptive_min, self.ev_adaptive_max, self.ev_adaptive_default, self.ev_adaptive_curr

    def set_ev_adaptive(self, value):
        self.ev_adaptive_curr = value
        self.settings_changed_callback()


    def get_wb_state(self):
        return self.wb_min, self.wb_max, self.wb_default, self.wb_curr

    def set_wb(self, value):
        self.wb_curr = value
        self.settings_changed_callback()



    def get_brightness_state(self):
        return self.brightness_min, self.brightness_max, self.brightness_default, self.brightness_curr
 
    def set_brightness(self, value):
        self.brightness_curr = value
        self.settings_changed_callback()

    def get_contrast_state(self):
        return self.contrast_min, self.contrast_max, self.contrast_default, self.contrast_curr
 
    def set_contrast(self, value):
        self.contrast_curr = value
        self.settings_changed_callback()


    def get_clarity_state(self):
        return self.clarity_min, self.clarity_max, self.clarity_default, self.clarity_curr
 
    def set_clarity(self, value):
        self.clarity_curr = value
        self.settings_changed_callback()


    def get_saturation_state(self):
        return self.saturation_min, self.saturation_max, self.saturation_default, self.saturation_curr
 
    def set_saturation(self, value):
        self.saturation_curr = value
        self.settings_changed_callback()


    def get_vibrance_state(self):
        return self.vibrance_min, self.vibrance_max, self.vibrance_default, self.vibrance_curr
 
    def set_vibrance(self, value):
        self.vibrance_curr = value
        self.settings_changed_callback()


    def get_equalisation_state(self):
        return self.equalisation_min, self.equalisation_max, self.equalisation_default, self.equalisation_curr
 
    def set_equalisation(self, value):
        self.equalisation_curr = value
        self.settings_changed_callback()


    def get_tones_state(self):
        return self.tones_min, self.tones_max, self.tones_default, self.tones_dark_curr, self.tones_mid_curr, self.tones_high_curr

    def set_tones_dark(self, value):
        self.tones_dark_curr = value
        self.settings_changed_callback()

    def set_tones_mid(self, value):
        self.tones_mid_curr = value
        self.settings_changed_callback()

    def set_tones_high(self, value):
        self.tones_high_curr = value
        self.settings_changed_callback()


    def get_colors_state(self):
        return self.colors_min, self.colors_max, self.colors_default, self.colors_red_curr, self.colors_green_curr, self.colors_blue_curr
    
    def set_colors_red(self, value):
        self.colors_red_curr = value
        self.settings_changed_callback()

    def set_colors_green(self, value):
        self.colors_green_curr = value
        self.settings_changed_callback()

    def set_colors_blue(self, value):
        self.colors_blue_curr = value
        self.settings_changed_callback()


    def get_blur_state(self):
        return self.blur_min, self.blur_max, self.blur_default, self.blur_curr
 
    def set_blur(self, value):
        self.blur_curr = value
        self.settings_changed_callback()

    def get_sharpen_state(self):
        return self.sharpen_min, self.sharpen_max, self.sharpen_default, self.sharpen_curr
 
    def set_sharpen(self, value):
        self.sharpen_curr = value
        self.settings_changed_callback()

    def get_bilateral_state(self):
        return self.bilateral_min, self.bilateral_max, self.bilateral_default, self.bilateral_curr
 
    def set_bilateral(self, value):
        self.bilateral_curr = value
        self.settings_changed_callback()

    def get_crop_state(self):
        return self.crop_modes, self.crop_default, self.crop_curr
    
    def set_crop_mode(self, value):
        self.crop_curr = value
        self.settings_changed_callback()

    def get_stacking_modes(self):
        return self.stacking_modes


    def settings_changed_callback(self):
        print("settings changed")
