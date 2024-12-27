import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QSpacerItem, QSizePolicy,
    QSlider, QPushButton, QGraphicsView, QGraphicsScene, QFileDialog, QListWidgetItem, QTabWidget)
from PyQt5.QtCore import Qt, QSize, QEvent, QObject, QCoreApplication
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPainter, QFont, QCursor
import pyqtgraph as pg
import os

from core_ import *

from ImageLoader import *

import traceback
from functools import partial


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



    def _make_photo_thumbnails_layout(self):
        layout = QVBoxLayout()
         
        # Photo viewer (central)
        self.photo_view = QGraphicsView()
        self.photo_scene = QGraphicsScene()
        self.photo_view.setScene(self.photo_scene)
        
        layout.addWidget(self.photo_view, stretch = 5)


        # Thumbnails list
        self.thumbnails_list = QListWidget()
        self.thumbnails_list.setViewMode(QListWidget.IconMode)
        self.thumbnails_list.setIconSize(QSize(100, 100))
        self.thumbnails_list.itemClicked.connect(self.thumbnail_clicked)

        layout.addWidget(self.thumbnails_list, stretch=1)


        return layout
    

    def _make_tool_box_layout(self):
        # Right-side layout
        layout = QVBoxLayout()

        # Histogram section
        self.histogram_widget = pg.PlotWidget()
        self.histogram_widget.setTitle("Histogram")
        self.histogram_widget.setLabel("left", "Frequency")
        self.histogram_widget.setLabel("bottom", "Pixel Intensity")
        layout.addWidget(self.histogram_widget, stretch=1)

        # Tool selection list
        self.tool_list = QListWidget()
        font = QFont()
        font.setPointSize(20)
        
        self.tool_list.setFont(font)

        self.tool_list.addItems(["Exposure", "Brightness and Contrast", "Colors", "Tones", "Filters", "Crop"])
        self.tool_list.currentItemChanged.connect(self.tool_selected)   
        layout.addWidget(self.tool_list, stretch=1)

        # Tool options 
        self.tool_options_layout = QVBoxLayout()
        self.tool_options_container = QWidget()
        self.tool_options_container.setLayout(self.tool_options_layout)
        layout.addWidget(self.tool_options_container, stretch=2)


        # split preview button
        split_preview_button = QPushButton("Split Preview")

        layout.addWidget(split_preview_button)
        split_preview_button.clicked.connect(self.on_split_preview_click)

        return layout


    def _make_stacking_layout(self):
        layout = QVBoxLayout()


        stacking_label = QLabel("Stacking Options")

        font = QFont()
        font.setPointSize(20)
        stacking_label.setFont(font)

        layout.addWidget(stacking_label)

        list_widget = QListWidget()
        list_widget.addItems(["mean", "max", "min", "median", "bracketing"])
        list_widget.setCurrentRow(0)

        # Tool selection list
        font = QFont()
        font.setPointSize(20)
        
        list_widget.setFont(font)

        layout.addWidget(list_widget)

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(spacer)
        

        slider = QSlider(Qt.Horizontal) 
        if self.core.is_loaded():
            slider.setRange(1, self.core.get_count() - self.core.get_curr_idx())
            slider.setValue(1)  
        else:
            slider.setRange(1, 2)
            slider.setValue(1)  
        label = QLabel("Photos count : 1")
        layout.addWidget(label)
        layout.addWidget(slider)

        button = QPushButton("Apply Stacking")
        layout.addWidget(button)

        slider.valueChanged.connect(lambda value: label.setText("Photos count : " + str(value)))

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(spacer)
        
        button.clicked.connect(lambda: self.on_stacking_click(list_widget, slider))

        layout.addStretch()

        return layout

    def _make_ai_layout(self):
        layout = QVBoxLayout()

        ai_label = QLabel("AI tools")

        font = QFont()
        font.setPointSize(20)
        ai_label.setFont(font)

        layout.addWidget(ai_label) 

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(spacer)

        button_smart_histogram = QPushButton("Smart Histogram")
        layout.addWidget(button_smart_histogram)
        button_night_photo = QPushButton("Night Photo")
        layout.addWidget(button_night_photo)
  

        layout.addStretch()

        return layout
    

    def _make_export_layout(self):
        layout = QVBoxLayout()

        quality_label = QLabel("Quality 98")

        #font = QFont()
        #font.setPointSize(20)
        #quality_label.setFont(font)

        layout.addWidget(quality_label)   


        quality_slider = QSlider(Qt.Horizontal)
        quality_slider.setRange(int(5), int(100))
        quality_slider.setValue(int(98))
        layout.addWidget(quality_slider)   

        quality_slider.valueChanged.connect(lambda : self.on_quality_change(quality_slider, quality_label))

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(spacer)
        

        button_jpg = QPushButton("Export image JPG")
        layout.addWidget(button_jpg)
        button_jpg.clicked.connect(lambda: self.on_export_image_button("jpg", quality_slider.value()))

        button_png = QPushButton("Export image PNG")    
        layout.addWidget(button_png)
        button_png.clicked.connect(lambda: self.on_export_image_button("png", quality_slider.value()))

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(spacer)


        timelapse_label = QLabel("Timelapse")

        font = QFont()
        font.setPointSize(20)
        timelapse_label.setFont(font)

        layout.addWidget(timelapse_label) 


        fps_label = QLabel("FPS 25")
        layout.addWidget(fps_label) 

        fps_slider = QSlider(Qt.Horizontal)
        fps_slider.setRange(int(10), int(60))
        fps_slider.setValue(int(25))
        layout.addWidget(fps_slider) 

        fps_slider.valueChanged.connect(lambda : self.on_fps_change(fps_slider, fps_label))

        button_timelapse = QPushButton("Export timelapse")
        layout.addWidget(button_timelapse)
        button_timelapse.clicked.connect(lambda: self.on_export_timelapse_button(fps_slider.value(), quality_slider.value()))


        layout.addStretch()

        return layout
    
    def _create_right_panel(self):
        if self.tool_box_layout is not None:
            self._clear_layout(self.tool_box_layout)

        if self.stacking_layout is not None:
            self._clear_layout(self.stacking_layout)

        if self.ai_layout is not None:
            self._clear_layout(self.ai_layout)

        if self.export_layout is not None:
            self._clear_layout(self.export_layout)

        if self.right_panel_tabs is not None:
            self.right_panel_tabs.clear()
            self.main_content_layout.removeWidget(self.right_panel_tabs)


        # right panel options
        self.tool_box_layout = self._make_tool_box_layout()
        #self.stacking_layout = self._make_stacking_layout()
        #self.ai_layout       = self._make_ai_layout()
        #self.export_layout   = self._make_export_layout()

        self.right_panel_tabs = QTabWidget()

        self.right_panel_tabs.setStyleSheet("QTabBar::tab { font-size: 16px; }")

        # Add tabs
        self.right_panel_tabs.addTab(self._wrap_layout_in_widget(self.tool_box_layout), "Tools")
        #self.right_panel_tabs.addTab(self._wrap_layout_in_widget(self.stacking_layout), "Stacking")
        #self.right_panel_tabs.addTab(self._wrap_layout_in_widget(self.ai_layout), "AI")
        #self.right_panel_tabs.addTab(self._wrap_layout_in_widget(self.export_layout), "Export")

        return self.right_panel_tabs

    
    def _wrap_layout_in_widget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    

    



        
    def __init__(self):
        super().__init__()
        
        self.core = Core()


        self.tool_box_layout    = None
        self.stacking_layout    = None
        self.ai_layout          = None
        self.export_layout      = None
        self.right_panel_tabs   = None

        

        self.setWindowTitle("Lens Lab")
        self.setGeometry(100, 100, 1800, 900)

        self.view_dims = ViewDims()

        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_content_layout = QHBoxLayout()

        self.photo_panel_layout = self._make_photo_thumbnails_layout()

        self.main_content_layout.addLayout(self.photo_panel_layout, stretch=15)

        self._create_right_panel()
  
        self.main_content_layout.addWidget(self.right_panel_tabs, stretch=5)


        self.main_layout.addLayout(self.main_content_layout, stretch=5)
        

        # Menu setup
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("File")

        open_folder_action = file_menu.addAction("Open Folder")
        open_folder_action.triggered.connect(self.open_folder)


        # mouse event handling
        event_filter = SceneEventFilter(self.photo_scene, self.core, self.view_dims, self.refresh_image)
        self.photo_scene.installEventFilter(event_filter)


        self.n_steps = 64

    def tool_selected(self, current, previous):
        print("tool_selected")
        # Update tool options dynamically based on selection

        #self.core.save_curr_settings()
        self.deinit_exposure_tool()
        self._clear_layout(self.tool_options_layout)
        
       
        if current.text() == "Exposure":
            self.init_exposure_tool()
        
           
            
        '''
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


        elif current.text() == "Filters":
            

            self.blur_label = QLabel("Gaussian blur 0")
            self.tool_options_layout.addWidget(self.blur_label)
            
            self.blur_slider = QSlider(Qt.Horizontal)
            self.blur_slider.setRange(int(0), int(100))
            self.blur_slider.setValue(int(0))
            self.tool_options_layout.addWidget(self.blur_slider)  

            self.blur_slider.valueChanged.connect(self.on_blur_change)
            

            self.sharpen_label = QLabel("Sharpen 0")
            self.tool_options_layout.addWidget(self.sharpen_label)
            
            self.sharpen_slider = QSlider(Qt.Horizontal)
            self.sharpen_slider.setRange(int(0), int(100))
            self.sharpen_slider.setValue(int(0))
            self.tool_options_layout.addWidget(self.sharpen_slider)     

            self.sharpen_slider.valueChanged.connect(self.on_sharpen_change)



            self.bilateral_label = QLabel("bilateral 0")
            self.tool_options_layout.addWidget(self.bilateral_label)
            
            self.bilateral_slider = QSlider(Qt.Horizontal)
            self.bilateral_slider.setRange(int(0), int(100))
            self.bilateral_slider.setValue(int(0))
            self.tool_options_layout.addWidget(self.bilateral_slider)     

            self.bilateral_slider.valueChanged.connect(self.on_bilateral_change)
            
        elif current.text() == "Crop":

            self.tool_options_layout.addWidget(QLabel("Cropping Options"))

            aspect_ratio_list = QListWidget()

            aspect_ratio_list.addItems(self.core.image.crop_modes)
            font = QFont()
            font.setPointSize(16)
            aspect_ratio_list.setFont(font)

            aspect_ratio_list.currentItemChanged.connect(self.on_aspect_ratio_selected)   
            self.tool_options_layout.addWidget(aspect_ratio_list)

            aspect_ratio_list.setCurrentRow(self.core.image.crop_curr)
        '''
            
        self.tool_options_layout.addStretch()

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            self.load_images(folder)

    def load_images(self, folder):
        
        print("loading images from ", folder)
        self.core.load_folder(folder)
        

        self._refresh()

    def _refresh(self, idx = -1):
        # select current    
        if idx != -1:
            self.core.set_curr_idx(idx)
        else:
            self.core.set_curr_idx(0)
            idx = 0

        self.core.load_curr_settings()


        # clear and update thumbnails
        self.thumbnails_list.clear()

        print("\n\nthumnails count ", len(self.core.loader.thumbnails), "\n\n")

        for n in range(len(self.core.loader.thumbnails)):
            x = self.core.loader.thumbnails[n]
            
            pixmap = self._numpy_to_qpixmap(x)
            
            item   = QListWidgetItem()

            icon = QIcon(pixmap)
            item.setIcon(icon)
            self.thumbnails_list.addItem(item)

        
        self._create_right_panel()

        

        self.main_content_layout.addWidget(self.right_panel_tabs, stretch=5)
        
        self.thumbnail_clicked(self.thumbnails_list.item(idx))
        self._clear_layout(self.tool_options_layout)


       

    

    def thumbnail_clicked(self, item):
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




    # exposure tool
    def init_exposure_tool(self):
        ev_min, ev_max, ev_curr = self.core.get_ev()

        self.ev_layout = QHBoxLayout()

        # slider
        self.ev_slider = QSlider(Qt.Horizontal)
        self.ev_slider.setRange(int(self.n_steps*ev_min), int(self.n_steps*ev_max))
        self.ev_slider.setValue(int(self.n_steps*ev_curr))
        self.ev_layout.addWidget(self.ev_slider)

        # button
        self.ev_reset_button = QPushButton("X")
        self.ev_reset_button.setFixedSize(30, 30)
        self.ev_layout.addWidget(self.ev_reset_button)

        # label
        self.ev_label = QLabel("Exposure " + str(round(ev_curr, 2)))
        self.tool_options_layout.addWidget(self.ev_label)

        self.tool_options_layout.addLayout(self.ev_layout)

        # callbacks
        self.ev_slider.valueChanged.connect(self.on_ev_change)
        self.ev_reset_button.clicked.connect(self.on_ev_reset)



        temperature_min, temperature_max, temperature_curr = self.core.get_temperature()
        self.temperature_layout = QHBoxLayout()

        # slider
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(int(self.n_steps*temperature_min), int(self.n_steps*temperature_max))
        self.temperature_slider.setValue(int(self.n_steps*temperature_curr))
        self.temperature_layout.addWidget(self.temperature_slider)            

        # button
        self.temperature_reset_button = QPushButton("X")
        self.temperature_reset_button.setFixedSize(30, 30)
        self.temperature_layout.addWidget(self.temperature_reset_button)  

        # label
        self.temperature_label = QLabel("Temperature (white balance) " + str(int(temperature_curr)))

        self.tool_options_layout.addWidget(self.temperature_label)   
        self.tool_options_layout.addLayout(self.temperature_layout)

        # callbacks 
        self.temperature_slider.valueChanged.connect(self.on_temperature_change)
        self.temperature_reset_button.clicked.connect(self.on_temperature_reset)



    def deinit_exposure_tool(self):

        if hasattr(self, "ev_slider"):
            self.ev_slider.valueChanged.disconnect()
            self.ev_slider.deleteLater()

        if hasattr(self, "ev_reset_button"):
            self.ev_reset_button.clicked.disconnect()
            self.ev_reset_button.deleteLater()

        if hasattr(self, "ev_layout"):
            self.ev_layout.deleteLater()


        if hasattr(self, "temperature_slider"):
            self.temperature_slider.valueChanged.disconnect()
            self.temperature_slider.deleteLater()

        if hasattr(self, "temperature_reset_button"):
            self.temperature_reset_button.clicked.disconnect()
            self.temperature_reset_button.deleteLater()

        if hasattr(self, "temperature_layout"):
            self.temperature_layout.deleteLater()

    def on_ev_change(self): 
        value = self.ev_slider.value()/self.n_steps
        self.core.set_ev(value)
        self.ev_label.setText("Exposure " + str(round(value, 2)))
        self.refresh_image()

    def on_ev_reset(self):
        value = self.core.reset_ev()
        self.ev_slider.setValue(int(self.n_steps*value))
        self.ev_label.setText("Exposure " + str(round(value, 2)))
        self.refresh_image()

    def on_temperature_change(self):
        value = self.temperature_slider.value()/self.n_steps
        self.core.set_temperature(value)
        self.temperature_slider.setValue(int(self.n_steps*value))
        self.temperature_label.setText("Temperature (white balance) " + str(int(value)))
        self.refresh_image()    

    def on_temperature_reset(self):
        value = self.core.reset_temperature()
        self.temperature_slider.setValue(int(self.n_steps*value))
        self.temperature_label.setText("Temperature (white balance) " + str(int(value)))
        self.refresh_image()





    def on_stacking_click(self, list_widget, slider):
        row_idx       = list_widget.currentRow()
        photos_count  = slider.value()

        stacking_type = list_widget.item(row_idx).text()

        print("count before add : ", self.core.get_count())
        self.core.stacking(stacking_type, photos_count)
        self.core.set_curr_idx(self.core.get_count()-1)

        self._refresh(self.core.get_count()-1)
    
    
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


    def on_blur_change(self):
        blur  = self.blur_slider.value()
        self.blur_label.setText("Gaussian Blur " + str(int(blur)))

        self.core.set_blur(blur/100.0)
        self.refresh_image()
        

    def on_sharpen_change(self):
        sharpen  = self.sharpen_slider.value()
        self.sharpen_label.setText("Gaussian Sharpen " + str(int(sharpen)))

        self.core.set_sharpen(sharpen/100.0)
        self.refresh_image()


    def on_bilateral_change(self):
        bilateral  = self.bilateral_slider.value()
        self.bilateral_label.setText("Bilateral filter " + str(int(bilateral)))

        self.core.set_bilateral(bilateral/100.0)
        self.refresh_image()

    
    def on_quality_change(self, slider, label):
        quality  = slider.value()
        label.setText("Quality " + str(int(quality)))

    def on_export_image_button(self, extension, quality):
        self.core.export_curr(extension, quality)

    def on_fps_change(self, slider, label):
        fps  = slider.value()
        label.setText("FPS " + str(int(fps)))

    def on_export_timelapse_button(self, fps, quality):
        self.core.export_time_lapse(fps, quality)

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
