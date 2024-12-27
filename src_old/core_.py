from ImageLoader import *
from Image       import *

from Bracketing  import *

import time

class Core:

    def __init__(self, tw = 100, th = 100):
        self.tw = tw
        self.th = th

    def is_loaded(self):
        if hasattr(self, "loader"):
            return True
        else:
            return False
        
    def load_folder(self, path):    
        self.loader     = ImageLoader(path + "/")
        self.loader.load_thumbnails(self.tw, self.th)

        self.current_idx= 0

        self.image = Image(self.loader[self.current_idx])

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
        self.image.update() 


    def export_curr(self, extension = None, quality = 99):
        path, file_name = self._split_file_name(self.current_idx)
        path = path + "/LensLabExported/"

        if os.path.exists(path) != True:
            os.makedirs(path)

        if extension is None:
            extension = "jpg"

        self.save_curr_settings()
        self.image.export(path + file_name, extension, quality)

    def export_time_lapse(self, fps=25, quality = 99):
        print("export time lapse in ", fps, " fps")

        path, _ = self._split_file_name(self.current_idx)
        file_name = path + "/LensLabExported/time_lapse.mp4"

        x = self.image.process_full_resolution(self.loader[0])
        height = x.shape[0]
        width  = x.shape[1]

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        #fourcc = cv2.VideoWriter_fourcc(*'H264')
        writer = cv2.VideoWriter(file_name, fourcc, fps, (width, height))

        photos_count = len(self.loader)
        for n in range(photos_count):
            time_start = time.time()

            y = self.image.process_full_resolution(self.loader[n])

            if y.shape[0] == height and y.shape[1] == width:
                image = numpy.clip(255*y, 0, 255).astype(numpy.uint8)
                writer.write(image)

            time_stop = time.time()

            eta = (time_stop - time_start)*(photos_count - n)
            eta = round(eta/60.0, 1)
            print("processing image ", n, " from ", photos_count, " eta ", eta, " min")

        writer.release()

        print("done\n")

    
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
        
    
    def split_preview_toogle(self):
        self.image.split_preview_toogle()
    

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
            print("unknown stacking : ", stacking_type)


        curr_name = self.loader.get_name(self.get_curr_idx())

        curr_name_prefix, curr_name_ext = curr_name.rsplit(".", 1)        

        result_name = curr_name_prefix + "_stacked_" + stacking_type + "." + curr_name_ext

        print("saving stacked image as : ", result_name)
        
        result_tmp = numpy.array(result*255, dtype=numpy.uint8)
        cv2.imwrite(result_name, result_tmp, [int(cv2.IMWRITE_JPEG_QUALITY), 99])
        
        self.loader.add_new(result_name)

        print("stacking done\n\n")  

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

    def set_blur(self, value):
        self.image.set_blur(value)

    def set_sharpen(self, value):
        self.image.set_sharpen(value)

    def set_bilateral(self, value):
        self.image.set_bilateral(value)

    def _split_file_name(self, idx):
        image_file_name = self.loader.get_name(idx)
        path, file_name = image_file_name.rsplit("/", 1)
        file_name       = file_name.rsplit(".", 1)[0]

        return path, file_name