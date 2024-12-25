from ImageLoader import *
from Image       import *

from Bracketing  import *

class Core:

    def __init__(self, tw = 100, th = 100):
        self.tw = tw
        self.th = th

        
    def load_folder(self, path):    
        self.loader     = ImageLoader(path + "/")
        self.thumbnails = self.loader.load_thumbnails(self.tw, self.th)

        self.current_idx= 0

        self.image = Image(self.loader[self.current_idx])

        self.image.load

    def get_count(self):
        return len(self.loader)

    def set_curr_idx(self, idx):
        self.current_idx = idx

        self.image = Image(self.loader[self.current_idx])

        return self.image.get_image()
    
   

    def save_curr_settings(self):
        path, file_name = self._split_file_name(self.current_idx)
        self.image.save(path + "/" + file_name + ".json")

    def load_curr_settings(self):
        path, file_name = self._split_file_name(self.current_idx)
        self.image.load(path + "/" + file_name + ".json")
    
    def get_curr_idx(self):
        return self.current_idx

    def get_curr_image(self):
        return self.image.get_image()

    def get_curr_histogram(self):
        return self.image.get_histogram()
    
    def get_ev(self):
        return self.image.get_ev()
    
    def reset_ev(self):
        self.image.set_ev(self.image.ev_default)
        return self.image.ev_default
    
    def get_temperature(self):
        return self.image.get_temperature()
    
    def reset_temperature(self):
        self.image.set_temperature(self.image.temperature_default)
        return self.image.temperature_default

    def get_brightness(self):
        return self.image.get_brightness()
    
    def reset_brightness(self):
        self.image.set_brightness(self.image.brightness_default)
        return self.image.brightness_default

    def get_contrast(self):
        return self.image.get_contrast()
    
    def reset_contrast(self):
        self.image.set_contrast(self.image.contrast_default)
        return self.image.contrast_default

    def get_saturation(self):
        return self.image.get_saturation()
    
    def reset_saturation(self):
        self.image.set_saturation(self.image.saturation_default)
        return self.image.saturation_default
    
    def get_vibrance(self):
        return self.image.get_vibrance()
    
    def reset_vibrance(self):
        self.image.set_vibrance(self.image.vibrance_default)
        return self.image.vibrance_default
    
    def get_tones(self):
        return self.image.get_tones()
    
    def reset_tones(self):
        self.image.set_tones(self.image.tones_default, self.image.tones_default, self.image.tones_default)
        return self.image.tones_default, self.image.tones_default, self.image.tones_default
    



    def get_equalisation(self):
        return self.image.get_equalisation()
    
    def reset_equalisation(self):
        self.image.set_equalisation(self.image.equalisation_default)
        return self.image.equalisation_default
        
    

    

    def stacking(self, stacking_type, photos_count, mask = None):
        print("core : stacking : ", stacking_type, photos_count)

        if stacking_type in ["mean", "max", "min"]:
            
            result = self.loader[self.get_curr_idx()]

            height = result.shape[0]
            width  = result.shape[1]
           
            for n in range(1, photos_count):
                tmp = self.loader[n + self.get_curr_idx()]

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
                tmp = self.loader[n + self.get_curr_idx()]

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
                tmp = self.loader[n + self.get_curr_idx()]

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
            result = self.get_curr_image().copy()
            print("unknown stacking : ",stacking_type )


        self.image = Image(result)

        print("stacking done")  

    def set_default(self):
        self.image.set_default()

    def set_ev(self, value):
        self.image.set_ev(value)

    def set_temperature(self, value):
        return self.image.set_temperature(value)
    
    

    def set_brightness(self, value):
        self.image.set_brightness(value)

    def set_contrast(self, value):
        self.image.set_contrast(value)

    def set_saturation(self, value):
        self.image.set_saturation(value)

    def set_vibrance(self, value):
        self.image.set_vibrance(value)

    def set_tones(self, shadows_curr, midtones_curr, highlight_curr):
        self.image.set_tones(shadows_curr, midtones_curr, highlight_curr)
      
    def set_equalisation(self, value):
        self.image.set_equalisation(value)

    

    def _split_file_name(self, idx):
        image_file_name = self.loader.get_name(idx)
        path, file_name = image_file_name.rsplit("/", 1)
        file_name       = file_name.rsplit(".", 1)[0]

        return path, file_name