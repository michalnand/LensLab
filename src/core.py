import numpy
import cv2

from ImageLoader    import *
from ImageSettings  import *
import Filters
import FilterStacking

import time

class Core(ImageSettings):

    def __init__(self):
        super().__init__()

        self.scale_ratio = 4

        # thumbnails size
        self.tw = 120 
        self.th = 120
        
        self.tool_names = []
        self.tool_names.append("Exposure")
        self.tool_names.append("Brightness and Contrast")
        self.tool_names.append("Colors")
        self.tool_names.append("Tones")
        self.tool_names.append("Filters")
        self.tool_names.append("Crop")

        self.image_settings = ImageSettings()

        self.split_preview = False


    def get_count(self):
        return len(self.loader)
    
    def get_curr_idx(self):
        return self.current_idx

    def toogle_split_preview(self):
        if self.split_preview:
            self.split_preview = False
        else:
            self.split_preview = True

        self.update_process()

        
    def register_photo_view_instance(self, photo_view_instance):
        self.photo_view_instance = photo_view_instance

    def register_tools_instance(self, tools_instance):
        self.tools_instance = tools_instance

    def register_stacking_instance(self, stacking_instance):
        self.stacking_instance = stacking_instance

    def register_export_instance(self, export_instance):
        self.export_instance = export_instance

    def get_tool_names(self):
        return self.tool_names
    
    def get_histogram(self, image):
        tmp = numpy.array(image*255, dtype=numpy.uint8)

        hist_size = 255

        histogram = numpy.zeros((4, hist_size))


        r = cv2.calcHist([tmp], [0], None, [hist_size], [0, 256])[:, 0]
        g = cv2.calcHist([tmp], [1], None, [hist_size], [0, 256])[:, 0]
        b = cv2.calcHist([tmp], [2], None, [hist_size], [0, 256])[:, 0]


        w = r + g + b
        w = w/(w.sum() + 1e-6)
            
        histogram[0] = w   
        histogram[1] = r/(r.sum() + 1e-6)
        histogram[2] = g/(g.sum() + 1e-6)
        histogram[3] = b/(b.sum() + 1e-6)

        # histogram smoothing
        window_size = 9
        kernel = numpy.ones(window_size) / window_size

        for n in range(histogram.shape[0]):
            histogram[n] = numpy.convolve(histogram[n], kernel, mode='same')
    
        return histogram
    
    def set_mouse_click(self, x, y):
        self.crop_x = numpy.clip(x, 0.0, 1.0)
        self.crop_y = numpy.clip(y, 0.0, 1.0)

        self.update_process()
       

    def _plot_crop_rectangle(self, img, crop_left, crop_right, crop_top, crop_bottom):   
        result = img.copy() 
        result[crop_top:crop_bottom, crop_left:crop_right, :] = 5.0*result[crop_top:crop_bottom, crop_left:crop_right, :]
        result/= 5.0    

        result = cv2.line(result, (crop_left, crop_top), (crop_right, crop_top), (0.8, 0.8, 0.8), 2)
        result = cv2.line(result, (crop_left, crop_bottom), (crop_right, crop_bottom), (0.8, 0.8, 0.8), 2)
        result = cv2.line(result, (crop_left, crop_top), (crop_left, crop_bottom), (0.8, 0.8, 0.8), 2)
        result = cv2.line(result, (crop_right, crop_top), (crop_right, crop_bottom), (0.8, 0.8, 0.8), 2)

        # Calculate the step size for splitting into thirds
        width = crop_right - crop_left
        height = crop_bottom - crop_top

        step_x = width // 3
        step_y = height // 3

        # Draw vertical lines for thirds
        for i in range(1, 3):  # 1 and 2 for the thirds
            x = crop_left + i * step_x
            result = cv2.line(result, (x, crop_top), (x, crop_bottom), (0.8, 0.8, 0.8), 1)

        # Draw horizontal lines for thirds
        for i in range(1, 3):  # 1 and 2 for the thirds
            y = crop_top + i * step_y
            result = cv2.line(result, (crop_left, y), (crop_right, y), (0.8, 0.8, 0.8), 1)

        return result

    
    def update_process(self):
        print("apply settings : update_process")

        self.image_curr = self._update(self.image_orig_small)
        self.histogram  = self.get_histogram(self.image_curr)

        if self.split_preview:
            self.image_curr = self._split_preview(self.image_orig_small, self.image_curr)

        center_x = self.image_curr.shape[1]*self.crop_x
        center_y = self.image_curr.shape[0]*self.crop_y

        crop_left, crop_right, crop_top, crop_bottom = self._get_crop_rectangle(self.image_orig_small.shape[1], self.image_orig_small.shape[0], center_x, center_y)
        self.image_curr = self._plot_crop_rectangle(self.image_curr.copy(), crop_left, crop_right, crop_top, crop_bottom)

        
        # refresh image view
        self.photo_view_instance.update_image(self.image_curr)
        self.tools_instance.update_histogram(self.histogram)


    def settings_changed_callback(self):
        self.update_process()

    def load_images(self, path):
        print("loading images from ", path)
        self.loader = ImageLoader(path + "/")
        self.loader.load_thumbnails(self.tw, self.th)

        self.current_idx = 0

        self.photo_view_instance.update_thumbnails(self.loader.thumbnails)
        
        #TODO : auto reload sliders
        #self.tools_instance.update_tool_status()

        self.set_curr_image(self.current_idx, False)        

   
    def set_curr_image(self, idx, save_settings = True):
        if save_settings:
            path, file_name = self._split_file_name(self.current_idx)
            self.save_settings(path + "/" + file_name + ".json")

        self.current_idx = idx

        self.image_orig         = self.loader[idx]
        self.image_orig_small   = cv2.resize(self.image_orig, (self.image_orig.shape[1]//self.scale_ratio, self.image_orig.shape[0]//self.scale_ratio))
        self.image_curr         = self.image_orig_small.copy()

        self.crop_x = 0.5
        self.crop_y = 0.5

        # load default settings
        self.set_default()
        
        # load actual settings if exists
        path, file_name = self._split_file_name(self.current_idx)
        self.load_settings(path + "/" + file_name + ".json")

        # update image
        self.update_process()

        # update gui
        self.stacking_instance.update_range()
        self.tools_instance.update()


        

    def stacking(self, stacking_type, photos_count):
        print("core stacking ", stacking_type, photos_count)

        idx = self.current_idx

        # process image stacking
        result = FilterStacking.stacking(stacking_type, self.loader, idx, photos_count)

        path, file_name = self._split_file_name(idx)
        file_name = path + file_name + "_stacked_" + stacking_type + ".jpg"

        result = numpy.array(result*255, dtype=numpy.uint8)
        cv2.imwrite(file_name, result, [int(cv2.IMWRITE_JPEG_QUALITY), 99])

        # load new image
        self.loader.add_new(file_name)
        self.set_curr_image(len(self.loader)-1)

        # refresh image view
        self.photo_view_instance.update_thumbnails(self.loader.thumbnails)
        self.photo_view_instance.update_image(self.image_curr)
        self.tools_instance.update_histogram(self.histogram)



    def export_image(self, extension, quality):
        path, file_name = self._split_file_name(self.current_idx)
        self.save_settings(path + "/" + file_name + ".json")

        path = path + "/LensLabExported/"

        if os.path.exists(path) != True:
            os.makedirs(path)


        file_name = path + file_name + "." + extension
        print("exporting to ", file_name)

        result = self._update(self.image_orig)

        # apply crop
        center_x = result.shape[1]*self.crop_x
        center_y = result.shape[0]*self.crop_y
        crop_left, crop_right, crop_top, crop_bottom = self._get_crop_rectangle(result.shape[1], result.shape[0], center_x, center_y)

        result = result[crop_top:crop_bottom, crop_left:crop_right, :]

        result = numpy.array(result*255, dtype=numpy.uint8)
        if extension == "jpg":
            cv2.imwrite(file_name, result, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        else:
            cv2.imwrite(file_name, result)

        print("exporting done\n")

    def export_timelapse(self, fps, quality):
        print("exporting time lapse in ", fps, " fps")

        path, _ = self._split_file_name(self.current_idx)

        path = path + "/LensLabExported/"
        if os.path.exists(path) != True:
            os.makedirs(path)

        file_name = path + "time_lapse.mp4"

       
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = None

        photos_count = len(self.loader)
        for n in range(photos_count):
            time_start = time.time()

            result = self._update(self.loader[n])

            # apply crop
            center_x = result.shape[1]*self.crop_x
            center_y = result.shape[0]*self.crop_y
            crop_left, crop_right, crop_top, crop_bottom = self._get_crop_rectangle(result.shape[1], result.shape[0], center_x, center_y)

            result = result[crop_top:crop_bottom, crop_left:crop_right, :]

            if writer is None:  
                height = result.shape[0]
                width  = result.shape[1]
                writer = cv2.VideoWriter(file_name, fourcc, fps, (width, height))

            if result.shape[0] == height and result.shape[1] == width:
                result = numpy.clip(255*result, 0, 255).astype(numpy.uint8)
                writer.write(result)

            time_stop = time.time()

            eta = (time_stop - time_start)*(photos_count - n)
            eta = round(eta/60.0, 1)
            print("processing image ", n, " from ", photos_count, " eta ", eta, " min")

        writer.release()

        print("exporting done\n")

    def _split_file_name(self, idx):
        image_file_name = self.loader.get_name(idx)
        path, file_name = image_file_name.rsplit("/", 1)
        file_name       = file_name.rsplit(".", 1)[0]

        return path, file_name
    

    def _update(self, x):
        x = x.copy()

        if self.ev_curr != self.ev_default:
            x = Filters.adjust_ev(x, self.ev_curr)

        if self.ev_adaptive_curr != self.ev_adaptive_default:
            x = Filters.adjust_ev_adaptive(x, self.ev_adaptive_curr)

        if self.wb_curr != self.wb_default:
            x = Filters.adjust_white_balance(x, self.wb_curr)

        if self.clarity_curr != self.clarity_default:
            x = Filters.adjust_clarity(x, self.clarity_curr)

        if self.dehaze_curr != self.dehaze_default:
            x = Filters.adjust_dehaze(x, self.dehaze_curr)
        
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
    

    def _split_preview(self, image_orig, image_curr):

        height = image_curr.shape[1]
        width  = image_curr.shape[1] 

        result = image_curr.copy()

        result[:, 0:width//2, :] = image_orig[:, 0:width//2, :]
        result = cv2.line(result, (width//2, 0), (width//2, height), (0.6, 0.6, 0.6), 2) 

        return result
    

    def _get_crop_rectangle(self, width, height, center_x = None, center_y = None):
        aspect_width  = self.crop_ratio_x[self.crop_curr]
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

        rect_left    = int(round(numpy.clip(rect_left,  0, width)))
        rect_right   = int(round(numpy.clip(rect_right, 0, width)))

        rect_top     = int(round(numpy.clip(rect_top,    0, height)))
        rect_bottom  = int(round(numpy.clip(rect_bottom, 0, height)))

        return rect_left, rect_right, rect_top, rect_bottom
    

    def ai_assistant(self):
        print("core AI")