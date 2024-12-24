import os
import cv2
import numpy

class ImageLoader:

    def __init__(self, root_path):
        files = os.listdir(root_path)

        self.files_list = []
        for file in files:
            if file.endswith("jpg") or file.endswith("JPG") or file.endswith("PNG") or file.endswith("png"):
                if file[0] != ".":
                    self.files_list.append(root_path + "/" + file)

        self.files_list.sort()

        print("files ")
        print(self.files_list)

    def load_thumbnails(self, width, height):
        n_count = len(self.files_list)
        self.thumbnails = numpy.zeros((n_count, height, width, 3), dtype=numpy.float32)

        for n in range(n_count):
            x = self._load(n)

            h_orig = x.shape[0]
            w_orig = x.shape[1]

            h_tar = height
            w_tar = width
            
            x = cv2.resize(x, (w_tar, h_tar))

            self.thumbnails[n] = x

        return self.thumbnails


    def __len__(self):
        return len(self.files_list)
    
    def __getitem__(self, idx):
        return self._load(idx)
        
    def _load(self, idx):
        x = cv2.imread(self.files_list[idx])
        x = numpy.array(x/255.0, dtype=numpy.float32)
        return x