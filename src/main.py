import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget,
    QSlider, QPushButton, QGraphicsView, QGraphicsScene, QFileDialog, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize, QEvent, QObject, QCoreApplication
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPainter, QFont, QCursor
import pyqtgraph as pg
import os

from core import *

from ImageLoader import *

import traceback


class ViewDims:
    def __init__(self): 
        self.view_width    = 100
        self.view_height   = 100
        self.pixmap_width  = 100
        self.pixmap_height = 100


class SceneEventFilter(QObject):
    def __init__(self, scene, core, view_dims, refresh_func):
        super().__init__(scene)
        self.scene      = scene
        self.core       = core
        self.view_dims  = view_dims
        self.refresh_func = refresh_func

    def eventFilter(self, watched, event):
        if event.type() == QEvent.GraphicsSceneMousePress:
            if event.button() == Qt.LeftButton:
                scene_pos = event.scenePos()
                x, y = self._compute_relative_pos(scene_pos)              
                self.core.image.set_crop_event(x, y, True)
                self.refresh_func()

                
            return True
        elif event.type() == QEvent.GraphicsSceneMouseRelease:
            if event.button() == Qt.LeftButton:                
                scene_pos = event.scenePos()
                #x, y = self._compute_relative_pos(scene_pos)  


            return True
        elif event.type() == QEvent.GraphicsSceneMouseMove:            
            scene_pos = event.scenePos()
            #x, y = self._compute_relative_pos(scene_pos)              
            #self.core.image.set_crop_event(x, y, False)
            #self.refresh_func()

            
            return True
        
        return super().eventFilter(watched, event)


    def _compute_relative_pos(self, scene_pos):
        center_x = self.view_dims.view_width/2.0
        center_y = self.view_dims.view_height/2.0

        mouse_x = scene_pos.x()
        mouse_y = scene_pos.y()

        left_edge  = center_x - self.view_dims.pixmap_width/2.0
        right_edge = center_x + self.view_dims.pixmap_width/2.0

        top_edge    = center_y - self.view_dims.pixmap_height/2.0
        bottom_edge = center_y + self.view_dims.pixmap_height/2.0

        x = numpy.clip(mouse_x, left_edge, right_edge)
        y = numpy.clip(mouse_y, top_edge, bottom_edge)

        x = x - left_edge
        y = y - top_edge

        x = numpy.clip(x/self.view_dims.pixmap_width, 0.0, 1.0)
        y = numpy.clip(y/self.view_dims.pixmap_height, 0.0, 1.0)

        return x, y

class PhotoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lens Lab")
        self.setGeometry(100, 100, 1800, 900)

        self.view_dims = ViewDims()

        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_content_layout = QHBoxLayout()

        # layout for photo view and thumbnails
        self.photo_thumbnails_layout = QVBoxLayout()

        # Photo viewer (central)
        self.photo_view = QGraphicsView()
        self.photo_scene = QGraphicsScene()
        self.photo_view.setScene(self.photo_scene)


        self.photo_thumbnails_layout.addWidget(self.photo_view, stretch=5)


        self.thumbnails_list = QListWidget()
        self.thumbnails_list.setViewMode(QListWidget.IconMode)
        self.thumbnails_list.setIconSize(QSize(100, 100))
        self.thumbnails_list.itemClicked.connect(self.thumbnail_clicked)

        self.photo_thumbnails_layout.addWidget(self.thumbnails_list, stretch=1)



        self.main_content_layout.addLayout(self.photo_thumbnails_layout, stretch=5)

        # Right-side layout
        self.right_layout = QVBoxLayout()

        # Histogram section
        self.histogram_widget = pg.PlotWidget()
        self.histogram_widget.setTitle("Histogram")
        self.histogram_widget.setLabel("left", "Frequency")
        self.histogram_widget.setLabel("bottom", "Pixel Intensity")
        self.right_layout.addWidget(self.histogram_widget, stretch=1)

        # Tool selection list
        self.tool_list = QListWidget()
        font = QFont()
        font.setPointSize(16)
        self.tool_list.setFont(font)

        self.tool_list.addItems(["Stacking", "Exposure", "Brightness and Contrast", "Colors", "Tones", "Crop", "Export"])
        self.tool_list.currentItemChanged.connect(self.tool_selected)   
        self.right_layout.addWidget(self.tool_list, stretch=1)

        # Tool options (customizable area)
        self.tool_options_layout = QVBoxLayout()
        self.tool_options_container = QWidget()
        self.tool_options_container.setLayout(self.tool_options_layout)
        self.right_layout.addWidget(self.tool_options_container, stretch=2)


        # split preview button
        split_preview_button = QPushButton("Split preview")

        self.right_layout.addWidget(split_preview_button)
        split_preview_button.clicked.connect(self.on_split_preview_click)


        self.main_content_layout.addLayout(self.right_layout, stretch=2)
        self.main_layout.addLayout(self.main_content_layout, stretch=5)


        # Menu setup
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("File")

        open_folder_action = file_menu.addAction("Open Folder")
        open_folder_action.triggered.connect(self.open_folder)

        open_image_action = file_menu.addAction("Open Image")
        open_image_action.triggered.connect(self.open_image)

        export_image_action = file_menu.addAction("Export Image")
        export_image_action.triggered.connect(self.export_image)

        export_folder_action = file_menu.addAction("Export Folder")
        export_folder_action.triggered.connect(self.export_folder)

        export_timelapse_action = file_menu.addAction("Export Timelapse")
        export_timelapse_action.triggered.connect(self.export_timelapse)

        self.core = Core()


        # mouse event handling
        event_filter = SceneEventFilter(self.photo_scene, self.core, self.view_dims, self.refresh_image)
        self.photo_scene.installEventFilter(event_filter)


        self.n_steps = 64

    def tool_selected(self, current, previous):
        # Update tool options dynamically based on selection

        self.core.image.set_crop_disabled()

        #self.core.save_curr_settings()
        self._clear_layout(self.tool_options_layout)
        
        n_steps = self.n_steps

        if current.text() == "Stacking":

            list_widget = QListWidget()
            list_widget.addItems(["mean", "max", "min", "median", "bracketing"])
            list_widget.setCurrentRow(0)
            self.tool_options_layout.addWidget(list_widget)

            slider = QSlider(Qt.Horizontal) 
            slider.setRange(1, self.core.get_count() - self.core.get_curr_idx())
            slider.setValue(1)  
            label = QLabel("Photos count : 1")
            self.tool_options_layout.addWidget(label)
            self.tool_options_layout.addWidget(slider)

            button = QPushButton("Apply Stacking")
            self.tool_options_layout.addWidget(button)

            slider.valueChanged.connect(lambda value: label.setText("Photos count : " + str(value)))

            button.clicked.connect(lambda: self.on_stacking_click(list_widget, slider))

        
       
        elif current.text() == "Exposure":
        
            ev_min, ev_max, ev_curr = self.core.get_ev()

            ev_layout = QHBoxLayout()

            # slider
            ev_slider = QSlider(Qt.Horizontal)
            ev_slider.setRange(int(n_steps*ev_min), int(n_steps*ev_max))
            ev_slider.setValue(int(n_steps*ev_curr))
            ev_layout.addWidget(ev_slider)

            # button
            ev_reset_button = QPushButton("X")
            ev_reset_button.setFixedSize(30, 30)
            ev_layout.addWidget(ev_reset_button)

            # label
            ev_label = QLabel("Exposure " + str(round(ev_curr, 2)))
            self.tool_options_layout.addWidget(ev_label)

            self.tool_options_layout.addLayout(ev_layout)

            # callbacks
            ev_slider.valueChanged.connect(lambda : self.on_ev_change(ev_label, ev_slider, ev_slider.value()/n_steps))
            ev_reset_button.clicked.connect(lambda: self.on_ev_change(ev_label, ev_slider, None))



            temperature_min, temperature_max, temperature_curr = self.core.get_temperature()
            temperature_layout = QHBoxLayout()

            # slider
            temperature_slider = QSlider(Qt.Horizontal)
            temperature_slider.setRange(int(n_steps*temperature_min), int(n_steps*temperature_max))
            temperature_slider.setValue(int(n_steps*temperature_curr))
            temperature_layout.addWidget(temperature_slider)            

            # button
            temperature_reset_button = QPushButton("X")
            temperature_reset_button.setFixedSize(30, 30)
            temperature_layout.addWidget(temperature_reset_button)  

            # label
            temperature_label = QLabel("Temperature (white balance) " + str(int(temperature_curr)))

            self.tool_options_layout.addWidget(temperature_label)   
            self.tool_options_layout.addLayout(temperature_layout)

            # callbacks
            temperature_slider.valueChanged.connect(lambda : self.on_temperature_change(temperature_label, temperature_slider, temperature_slider.value()/n_steps))
            temperature_reset_button.clicked.connect(lambda: self.on_temperature_change(temperature_label, temperature_slider, None))

            

        elif current.text() == "Brightness and Contrast":

            brightness_min, brightness_max, brightness_curr = self.core.get_brightness()
            brightness_layout = QHBoxLayout()

            # slider
            brightness_slider = QSlider(Qt.Horizontal)
            brightness_slider.setRange(int(n_steps*brightness_min), int(n_steps*brightness_max))
            brightness_slider.setValue(int(n_steps*brightness_curr))
            brightness_layout.addWidget(brightness_slider)            

            # button
            brightness_reset_button = QPushButton("X")
            brightness_reset_button.setFixedSize(30, 30)
            brightness_layout.addWidget(brightness_reset_button)  

            # label
            brightness_label = QLabel("Brightness " + str(round(brightness_curr, 2)))

            self.tool_options_layout.addWidget(brightness_label)   
            self.tool_options_layout.addLayout(brightness_layout)

            # callbacks
            brightness_slider.valueChanged.connect(lambda : self.on_brightness_change(brightness_label, brightness_slider, brightness_slider.value()/n_steps))
            brightness_reset_button.clicked.connect(lambda: self.on_brightness_change(brightness_label, brightness_slider, None))



            contrast_min, contrast_max, contrast_curr = self.core.get_contrast()
            contrast_layout = QHBoxLayout()

            # slider
            contrast_slider = QSlider(Qt.Horizontal)
            contrast_slider.setRange(int(n_steps*contrast_min), int(n_steps*contrast_max))
            contrast_slider.setValue(int(n_steps*contrast_curr))
            contrast_layout.addWidget(contrast_slider)            

            # button
            contrast_reset_button = QPushButton("X")
            contrast_reset_button.setFixedSize(30, 30)
            contrast_layout.addWidget(contrast_reset_button)  

            # label
            contrast_label = QLabel("Contrast " + str(round(contrast_curr, 2)))

            self.tool_options_layout.addWidget(contrast_label)   
            self.tool_options_layout.addLayout(contrast_layout)

            # callbacks
            contrast_slider.valueChanged.connect(lambda : self.on_contrast_change(contrast_label, contrast_slider, contrast_slider.value()/n_steps))
            contrast_reset_button.clicked.connect(lambda: self.on_contrast_change(contrast_label, contrast_slider, None))

        

        elif current.text() == "Colors":




            saturation_min, saturation_max, saturation_curr = self.core.get_saturation()
            saturation_layout = QHBoxLayout()

            # slider
            saturation_slider = QSlider(Qt.Horizontal)
            saturation_slider.setRange(int(n_steps*saturation_min), int(n_steps*saturation_max))
            saturation_slider.setValue(int(n_steps*saturation_curr))
            saturation_layout.addWidget(saturation_slider)            

            # button
            saturation_reset_button = QPushButton("X")
            saturation_reset_button.setFixedSize(30, 30)
            saturation_layout.addWidget(saturation_reset_button)  

            # label
            saturation_label = QLabel("Saturation " + str(round(saturation_curr, 2)))

            self.tool_options_layout.addWidget(saturation_label)   
            self.tool_options_layout.addLayout(saturation_layout)

            # callbacks
            saturation_slider.valueChanged.connect(lambda : self.on_saturation_change(saturation_label, saturation_slider, saturation_slider.value()/n_steps))
            saturation_reset_button.clicked.connect(lambda: self.on_saturation_change(saturation_label, saturation_slider, None))

            


            vibrance_min, vibrance_max, vibrance_curr = self.core.get_vibrance()
            vibrance_layout = QHBoxLayout()

            # slider
            vibrance_slider = QSlider(Qt.Horizontal)
            vibrance_slider.setRange(int(n_steps*vibrance_min), int(n_steps*vibrance_max))
            vibrance_slider.setValue(int(n_steps*vibrance_curr))
            vibrance_layout.addWidget(vibrance_slider)            

            # button
            vibrance_reset_button = QPushButton("X")
            vibrance_reset_button.setFixedSize(30, 30)
            vibrance_layout.addWidget(vibrance_reset_button)  

            # label
            vibrance_label = QLabel("Vibrance " + str(round(vibrance_curr, 2)))

            self.tool_options_layout.addWidget(vibrance_label)   
            self.tool_options_layout.addLayout(vibrance_layout)

            # callbacks
            vibrance_slider.valueChanged.connect(lambda : self.on_vibrance_change(vibrance_label, vibrance_slider, vibrance_slider.value()/n_steps))
            vibrance_reset_button.clicked.connect(lambda: self.on_vibrance_change(vibrance_label, vibrance_slider, None))

            
            
            
            
            equalisation_min, equalisation_max, equalisation_curr = self.core.get_equalisation()
            equalisation_layout = QHBoxLayout()

            # slider
            equalisation_slider = QSlider(Qt.Horizontal)
            equalisation_slider.setRange(int(n_steps*equalisation_min), int(n_steps*equalisation_max))
            equalisation_slider.setValue(int(n_steps*equalisation_curr))
            equalisation_layout.addWidget(equalisation_slider)            

            # button
            equalisation_reset_button = QPushButton("X")
            equalisation_reset_button.setFixedSize(30, 30)
            equalisation_layout.addWidget(equalisation_reset_button)  

            # label 
            equalisation_label = QLabel("Equalisation " + str(round(equalisation_curr, 2)))

            self.tool_options_layout.addWidget(equalisation_label)   
            self.tool_options_layout.addLayout(equalisation_layout)

            # callbacks
            equalisation_slider.valueChanged.connect(lambda : self.on_equalisation_change(equalisation_label, equalisation_slider, equalisation_slider.value()/n_steps))
            equalisation_reset_button.clicked.connect(lambda: self.on_equalisation_change(equalisation_label, equalisation_slider, None))

           
        elif current.text() == "Tones":


            tones_min, tones_max, shadows_curr, midtones_curr, highlights_curr = self.core.get_tones()
            shadow_layout = QHBoxLayout()

            # slider
            slider_s = QSlider(Qt.Horizontal)
            slider_s.setRange(int(n_steps*tones_min), int(n_steps*tones_max))
            slider_s.setValue(int(n_steps*shadows_curr))
            shadow_layout.addWidget(slider_s)            

            # button
            shadow_reset_button = QPushButton("X")
            shadow_reset_button.setFixedSize(30, 30)
            shadow_layout.addWidget(shadow_reset_button)  

            # label
            label_s = QLabel("Shadows " + str(round(shadows_curr, 2)))

            self.tool_options_layout.addWidget(label_s)   
            self.tool_options_layout.addLayout(shadow_layout)


            midtones_layout = QHBoxLayout()

            # slider
            slider_m = QSlider(Qt.Horizontal)
            slider_m.setRange(int(n_steps*tones_min), int(n_steps*tones_max))
            slider_m.setValue(int(n_steps*midtones_curr))
            midtones_layout.addWidget(slider_m)            

            # button
            midtones_reset_button = QPushButton("X")
            midtones_reset_button.setFixedSize(30, 30)
            midtones_layout.addWidget(midtones_reset_button)  

            # label
            label_m = QLabel("Midtones " + str(round(midtones_curr, 2)))

            self.tool_options_layout.addWidget(label_m)   
            self.tool_options_layout.addLayout(midtones_layout)




            highlights_layout = QHBoxLayout()

            # slider
            slider_h = QSlider(Qt.Horizontal)
            slider_h.setRange(int(n_steps*tones_min), int(n_steps*tones_max))
            slider_h.setValue(int(n_steps*highlights_curr))
            highlights_layout.addWidget(slider_h)            

            # button
            highlights_reset_button = QPushButton("X")
            highlights_reset_button.setFixedSize(30, 30)
            highlights_layout.addWidget(highlights_reset_button)  

            # label
            label_h = QLabel("highlights " + str(round(highlights_curr, 2)))

            self.tool_options_layout.addWidget(label_h)   
            self.tool_options_layout.addLayout(highlights_layout)





            # callbacks
            slider_s.valueChanged.connect(lambda : self.on_tones_change(label_s, label_m, label_h, slider_s, slider_m, slider_h, slider_s.value()/n_steps, slider_m.value()/n_steps, slider_h.value()/n_steps))
            slider_m.valueChanged.connect(lambda : self.on_tones_change(label_s, label_m, label_h, slider_s, slider_m, slider_h, slider_s.value()/n_steps, slider_m.value()/n_steps, slider_h.value()/n_steps))
            slider_h.valueChanged.connect(lambda : self.on_tones_change(label_s, label_m, label_h, slider_s, slider_m, slider_h, slider_s.value()/n_steps, slider_m.value()/n_steps, slider_h.value()/n_steps))
            
            
            shadow_reset_button.clicked.connect(lambda: self.on_tones_change(label_s, label_m, label_h, slider_s, slider_m, slider_h, None, None, None))
            midtones_reset_button.clicked.connect(lambda: self.on_tones_change(label_s, label_m, label_h, slider_s, slider_m, slider_h, None, None, None))
            highlights_reset_button.clicked.connect(lambda: self.on_tones_change(label_s, label_m, label_h, slider_s, slider_m, slider_h, None, None, None))

            
        elif current.text() == "Crop":

            self.core.image.set_crop_enabled()

            self.tool_options_layout.addWidget(QLabel("Cropping Options"))

            aspect_ratio_list = QListWidget()

            aspect_ratio_list.addItems(self.core.image.crop_modes)
            font = QFont()
            font.setPointSize(16)
            aspect_ratio_list.setFont(font)

            aspect_ratio_list.currentItemChanged.connect(self.on_aspect_ratio_selected)   
            self.tool_options_layout.addWidget(aspect_ratio_list)

            aspect_ratio_list.setCurrentRow(self.core.image.crop_curr)

            

        # image export, or time-lapse export
        elif current.text() == "Export":
            button_jpg = QPushButton("Export image JPG")
            self.tool_options_layout.addWidget(button_jpg)
            button_jpg.clicked.connect(lambda: self.on_export_image_button("jpg"))

            button_png = QPushButton("Export image PNG")    
            self.tool_options_layout.addWidget(button_png)
            button_png.clicked.connect(lambda: self.on_export_image_button("png"))

        self.tool_options_layout.addStretch()

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            self.load_images(folder)

    def open_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file:
            self.display_image(file)

    def export_image(self):
        QFileDialog.getSaveFileName(self, "Export Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")

    def export_folder(self):
        QFileDialog.getExistingDirectory(self, "Export Folder")

    def export_timelapse(self):
        QFileDialog.getSaveFileName(self, "Export Timelapse", "", "Videos (*.mp4 *.avi)")

    def load_images(self, folder):
        self._clear_layout(self.tool_options_layout)

        print("loading images from ", folder)
        self.core.load_folder(folder)
        
        self.thumbnails_list.clear()

        for n in range(len(self.core.thumbnails)):
            x = self.core.thumbnails[n]
            
            pixmap = self._numpy_to_qpixmap(x)
            
            item   = QListWidgetItem()

            icon = QIcon(pixmap)
            item.setIcon(icon)
            self.thumbnails_list.addItem(item)

        self.core.set_curr_idx(0)
        self.core.load_curr_settings()
        self.thumbnail_clicked(self.thumbnails_list.item(0))

    def thumbnail_clicked(self, item):
        self.tool_list.setCurrentRow(0)
        self.tool_list.setCurrentRow(1)
        self.core.save_curr_settings()

        self._clear_layout(self.tool_options_layout)

        index = self.thumbnails_list.row(item)

        self.core.set_curr_idx(index)
        self.core.load_curr_settings()

        x    = self.core.get_curr_image()
        hist = self.core.get_curr_histogram()

        self.display_image(x)
        self.update_histogram(hist)
    

    def refresh_image(self):
        x    = self.core.get_curr_image()
        hist = self.core.get_curr_histogram()

        self.display_image(x)
        self.update_histogram(hist) 


    def display_image(self, x):
        pixmap = self._numpy_to_qpixmap(x)
        
        self.photo_scene.clear()    
        self.photo_scene.addPixmap(pixmap)
        self.photo_view.fitInView(self.photo_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
        self.photo_scene.clear()

        
        # Resize pixmap to fit within view while keeping aspect ratio and padding with zeros
        view_width = self.photo_view.width()
        view_height = self.photo_view.height()

        scaled_pixmap = pixmap.scaled(view_width, view_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        padded_image = QImage(view_width, view_height, QImage.Format_ARGB32)
        padded_image.fill(Qt.black)  # Fill with black (or zeros)


        self.view_dims.view_width    = self.photo_view.width()
        self.view_dims.view_height   = self.photo_view.height()
        self.view_dims.pixmap_width  = scaled_pixmap.width()
        self.view_dims.pixmap_height = scaled_pixmap.height()


        painter = QPainter(padded_image)
        x_offset = (view_width - scaled_pixmap.width()) // 2
        y_offset = (view_height - scaled_pixmap.height()) // 2
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        painter.end()

        self.photo_scene.addPixmap(QPixmap.fromImage(padded_image))
        self.photo_view.setScene(self.photo_scene)
        self.photo_view.fitInView(self.photo_scene.itemsBoundingRect(), Qt.KeepAspectRatio)


    def update_histogram(self, histogram):
       
        all     = histogram[0]
        red     = histogram[1]
        green   = histogram[2]
        blue    = histogram[3]

        self.histogram_widget.clear()
        self.histogram_widget.plot(all, pen=pg.mkPen("w"))
        self.histogram_widget.plot(red, pen=pg.mkPen("r"))
        self.histogram_widget.plot(green, pen=pg.mkPen("g"))
        self.histogram_widget.plot(blue, pen=pg.mkPen("b"))


    def _numpy_to_qpixmap(self, x):
        x_tmp = numpy.array(x*255, dtype=numpy.uint8)
        height, width, channels = x_tmp.shape
        bytes_per_line = channels * width
        qimage = QImage(x_tmp.data, width, height, bytes_per_line, QImage.Format_BGR888)
        return QPixmap.fromImage(qimage)    

           

    def on_split_preview_click(self):
        self.core.split_preview_toogle()

        self.refresh_image()

    def on_stacking_click(self, list_widget, slider):
        row_idx       = list_widget.currentRow()
        photos_count  = slider.value()

        stacking_type = list_widget.item(row_idx).text()

        self.core.stacking(stacking_type, photos_count)

        self.refresh_image()
    
    def on_ev_change(self, label, slider, value):
        if value is not None:
            self.core.set_ev(value)
        else:
            value = self.core.reset_ev()
            slider.setValue(int(self.n_steps*value))
        label.setText("Exposure " + str(round(value, 2)))

        self.refresh_image()

    def on_temperature_change(self, label, slider, value):
        if value is not None:
            self.core.set_temperature(value)
        else:
            value = self.core.reset_temperature()
            slider.setValue(int(self.n_steps*value))

        label.setText("Temperature (white balance) " + str(int(value)))

        self.refresh_image()




    def on_brightness_change(self, label, slider, value):
        if value is not None:
            self.core.set_brightness(value)
        else:
            value = self.core.reset_brightness()
            slider.setValue(int(self.n_steps*value))

        label.setText("Brightness " + str(round(value, 2)))
    
        self.refresh_image()


    def on_contrast_change(self, label, slider, value):
        if value is not None:
            self.core.set_contrast(value)
        else:
            value = self.core.reset_contrast()
            slider.setValue(int(self.n_steps*value))

        label.setText("Contrast " + str(round(value, 2)))
    
        self.refresh_image()


    def on_saturation_change(self, label, slider, value):
        if value is not None:
            self.core.set_saturation(value)
        else:
            value = self.core.reset_saturation()
            slider.setValue(int(self.n_steps*value))

        label.setText("Saturation " + str(round(value, 2)))
    
        self.refresh_image()


    def on_vibrance_change(self, label, slider, value):
        if value is not None:
            self.core.set_vibrance(value)
        else:
            value = self.core.reset_vibrance()
            slider.setValue(int(self.n_steps*value))

        label.setText("Vibrance " + str(round(value, 2)))
    
        self.refresh_image()


    def on_tones_change(self, label_s, label_m, label_h, slider_s, slider_m, slider_h, value_s, value_m, value_h):
        if value_s is not None:
            self.core.set_tones(value_s, value_m, value_h)
        else:
            value_s, value_m, value_h = self.core.reset_tones()
            slider_s.setValue(int(self.n_steps*value_s))
            slider_m.setValue(int(self.n_steps*value_m))
            slider_h.setValue(int(self.n_steps*value_h))

        label_s.setText("Shadows " + str(round(value_s, 2)))
        label_m.setText("Midtones " + str(round(value_m, 2)))
        label_h.setText("Highlights " + str(round(value_h, 2)))
    
        self.refresh_image()


    def on_equalisation_change(self, label, slider, value):
        if value is not None:
            self.core.set_equalisation(value)
        else:
            value = self.core.reset_equalisation()
            slider.setValue(int(self.n_steps*value))

        label.setText("Equalisation " + str(round(value, 2)))
    
        self.refresh_image()

    def on_export_image_button(self, extension):
        self.core.export_curr(extension)

    def on_aspect_ratio_selected(self, current, previous):
        self.core.image.set_crop_aspect_ratio(current.text())
        self.refresh_image()


    

    def _clear_layout(self, layout):
        while layout.count():  # Loop until no items are left in the layout
            item = layout.takeAt(0)  # Take the first item
        
            # Check if the item is a widget
            if widget := item.widget():
                widget.deleteLater()  # Delete the widget
        
            # Check if the item is a layout
            elif sub_layout := item.layout():
                self._clear_layout(sub_layout)  # Recursively clear the sub-layout

            else:
                print("_clear_layout unknown item ", item)

            del item

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PhotoEditor()
    editor.show()
    sys.exit(app.exec_())
