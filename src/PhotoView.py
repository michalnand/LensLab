from PyQt5.QtCore import Qt, QSize, QObject, QEvent
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QListWidget, QListWidgetItem, QPushButton)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPainter

import numpy



class SceneEventFilter(QObject):
    def __init__(self, scene, callback_func = None):
        super().__init__(scene)

        self.callback_func = callback_func

    def eventFilter(self, watched, event):
        if event.type() == QEvent.GraphicsSceneMousePress:
            if event.button() == Qt.LeftButton:
                scene_pos = event.scenePos()
                mouse_x = scene_pos.x()
                mouse_y = scene_pos.y()

                if self.callback_func is not None:
                    self.callback_func(mouse_x, mouse_y)
                
                
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

class PhotoView(QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.core.register_photo_view_instance(self)

        self.main_widget    = QWidget()
        self.main_layout    = QVBoxLayout(self.main_widget)

        # Photo viewer (central)
        self.photo_view = QGraphicsView()
        self.photo_scene = QGraphicsScene()
        self.photo_view.setScene(self.photo_scene)
        
        event_filter = SceneEventFilter(self.photo_scene, self.on_photo_mouse_click)
        self.photo_scene.installEventFilter(event_filter)

        self.main_layout.addWidget(self.photo_view, stretch = 5)

        # Thumbnails list   
        self.thumbnails_list = QListWidget()
        self.thumbnails_list.setViewMode(QListWidget.IconMode)
        self.thumbnails_list.setIconSize(QSize(120, 120))
        self.thumbnails_list.itemClicked.connect(self.on_thumbnail_clicked)


        self.main_layout.addWidget(self.thumbnails_list, stretch=1)

    def get(self):
        return self.main_widget
    

    def on_thumbnail_clicked(self, item):
        index = self.thumbnails_list.row(item)

        self.core.set_curr_image(index)

    def on_photo_mouse_click(self, mouse_x, mouse_y):
        # compute to relative position
        center_x = self.view_width/2.0
        center_y = self.view_height/2.0

        left_edge  = center_x - self.pixmap_width/2.0
        right_edge = center_x + self.pixmap_width/2.0

        top_edge    = center_y - self.pixmap_height/2.0
        bottom_edge = center_y + self.pixmap_height/2.0

        x = numpy.clip(mouse_x, left_edge, right_edge)
        y = numpy.clip(mouse_y, top_edge, bottom_edge)

        x = x - left_edge
        y = y - top_edge

        x = numpy.clip(x/self.pixmap_width, 0.0, 1.0)
        y = numpy.clip(y/self.pixmap_height, 0.0, 1.0)

        self.core.set_mouse_click(x, y)


    def update_thumbnails(self, thumbnails):
        # clear and update thumbnails
        self.thumbnails_list.clear()

        for n in range(len(thumbnails)):
        
            x = thumbnails[n]

            print("add thumbnail ", n, x.shape)
            
            pixmap = self._numpy_to_qpixmap(x)
            
            item   = QListWidgetItem()

            icon = QIcon(pixmap)
            item.setIcon(icon)
            self.thumbnails_list.addItem(item)

    def update_image(self, image):
        pixmap = self._numpy_to_qpixmap(image)
        
        self.photo_scene.clear()    
        self.photo_scene.addPixmap(pixmap)
        self.photo_view.fitInView(self.photo_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
        self.photo_scene.clear()

        
        # Resize pixmap to fit within view while keeping aspect ratio and padding with zeros
        view_width = self.photo_view.width()
        view_height = self.photo_view.height()

        scaled_pixmap = pixmap.scaled(view_width, view_height, Qt.KeepAspectRatio, Qt.FastTransformation)
        padded_image = QImage(view_width, view_height, QImage.Format_ARGB32)
        padded_image.fill(Qt.black)  # Fill with black (or zeros)


        self.view_width    = self.photo_view.width()
        self.view_height   = self.photo_view.height()
        self.pixmap_width  = scaled_pixmap.width()
        self.pixmap_height = scaled_pixmap.height()


        painter = QPainter(padded_image)
        x_offset = (view_width - scaled_pixmap.width()) // 2
        y_offset = (view_height - scaled_pixmap.height()) // 2
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        painter.end()

        self.photo_scene.addPixmap(QPixmap.fromImage(padded_image))
        self.photo_view.setScene(self.photo_scene)
        self.photo_view.fitInView(self.photo_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

        

    
    def _numpy_to_qpixmap(self, x):
        x_tmp = numpy.array(x*255, dtype=numpy.uint8)
        height, width, channels = x_tmp.shape
        bytes_per_line = channels * width
        qimage = QImage(x_tmp.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimage)    