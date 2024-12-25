import os
import cv2
import numpy

class ImageLoader:

    def __init__(self, root_path):
        self.root_path = root_path
        files = os.listdir(root_path)

        self.files_list = []
        for file in files:
            if self._check_file_name(file):
                if file[0] != ".":
                    self.files_list.append(root_path + "/" + file)

        self.files_list.sort()

        print("files ")
        print(self.files_list)

    def load_thumbnails(self, width, height):
        n_count = len(self.files_list)
        self.thumbnails = numpy.zeros((n_count, height, width, 3), dtype=numpy.float32)

        for n in range(n_count):
            self.thumbnails[n] = self._load_thumbnail(n, width, height)

        return self.thumbnails

    def add_new(self, file_name):
        if self._check_file_name(file_name):
            self.files_list.append(self.root_path + "/" + file_name)

            x = self._load_thumbnail(self.files_list, self.thumbnails[0].shape[0], self.thumbnails[0].shape[1])
            x = numpy.expand_dims(x, 0)
            self.thumbnails = numpy.vstack([self.thumbnails, x])

    def __len__(self):
        return len(self.files_list)
    
    def __getitem__(self, idx):
        return self._load(idx)
    
    def get_image(self, idx):
        return self._load(idx)
    
    def get_name(self, idx):
        return self.files_list[idx]
        
    def _load(self, idx):
        x = cv2.imread(self.files_list[idx])
        x = numpy.array(x/255.0, dtype=numpy.float32)
        return x
    
    def _load_thumbnail(self, idx, width, height):
        x = self._load(idx)

        h_orig = x.shape[0]
        w_orig = x.shape[1]

        h_tar = height
        w_tar = width
        
        x = cv2.resize(x, (w_tar, h_tar))

        return x
    

    def _check_file_name(self, file_name):
        if file_name.endswith("jpg") or file_name.endswith("JPG") or file_name.endswith("PNG") or file_name.endswith("png"):
            return True
        else:
            return False