import numpy
import cv2

from Adjustment import *

class PhotoToolBoxEnv:


    def __init__(self):
        self.adjustment = Adjustment()

    def get_actions_count(self):
        return self.adjustment.get_count()

    def reset(self):
        # load random target image
        self.image_target =  self._sample_image()

        # apply random distortion
        dist_adjustment = Adjustment()
        #dist_adjustment.random_adjustment()
        self.image_distorted =self.image_target.copy() #dist_adjustment.apply_adjustment(self.image_target)

        # reinitialise agent's adjustment to default
        self.adjustment.default_adjustment()
        
        # episode steps
        self.steps      = 0
        self.max_steps  = 8

        return self._get_state(self.image_distorted, self.image_distorted)
    

    def step(self, action):
        
        # modify adjustment by agents action
        self.adjustment.set_dadjustment(0.0000001*action)

        # reconstruct image by current tools settings
        image_restored = self.adjustment.apply_adjustment(self.image_distorted)

        # compute relative error and reward
        diff    = numpy.abs(self.image_target - image_restored)
        error   = (diff/(self.image_target + 10e-8)).mean()
        reward  = 1.0 - error

        self.steps+= 1
        if self.steps >= self.max_steps:
            done = True
        else:
            done = False

        return self._get_state(self.image_distorted, image_restored), reward, done
        

    def _sample_image(self):
        return numpy.random.rand(256, 256, 3).astype(numpy.float32)
        

    def _get_state(self, image_a, image_b):
        features_initial    = self._compute_features(image_a)
        features_curr       = self._compute_features(image_b)    

        n_features          = features_initial.shape[0]

        positional_encoding = numpy.arange(n_features)/(n_features - 1.0)
        positional_encoding = numpy.expand_dims(positional_encoding, 1)

        result = numpy.concatenate([positional_encoding, features_initial, features_curr], axis=1)

        return result
    

    def _compute_features(self, x):
        grayscale = cv2.cvtColor(x, cv2.COLOR_RGB2GRAY)

        hist_r = self._compute_histogram(x[:, :, 0])
        hist_g = self._compute_histogram(x[:, :, 1])
        hist_b = self._compute_histogram(x[:, :, 2])

        sobel_x = cv2.Sobel(grayscale, cv2.CV_32F, dx=1, dy=0, ksize=3)
        sobel_x = self._normalise_edges(sobel_x)
        sobel_y = cv2.Sobel(grayscale, cv2.CV_32F, dx=0, dy=1, ksize=3)
        sobel_y = self._normalise_edges(sobel_y)

        hist_sobel_x = self._compute_histogram(sobel_x)
        hist_sobel_y = self._compute_histogram(sobel_y)

        colorfulness        = self._compute_colorfulness(x)
        hist_colorfulness   = self._compute_histogram(colorfulness)


        mean_r = numpy.ones((hist_r.shape[0], 1))*x[:, :, 0].mean()
        std_r  = numpy.ones((hist_r.shape[0], 1))*x[:, :, 0].std()

        mean_g = numpy.ones((hist_g.shape[0], 1))*x[:, :, 1].mean()
        std_g  = numpy.ones((hist_g.shape[0], 1))*x[:, :, 1].std()

        mean_b = numpy.ones((hist_b.shape[0], 1))*x[:, :, 2].mean()
        std_b  = numpy.ones((hist_b.shape[0], 1))*x[:, :, 2].std()

        features = numpy.concatenate([mean_r, mean_g, mean_b, std_r, std_g, std_b, hist_r, hist_g, hist_b, hist_sobel_x, hist_sobel_y, hist_colorfulness], axis=1)

        return features
    

    def _compute_histogram(self, x):
        tmp = numpy.array(x*255, dtype=numpy.uint8)

        # compute histogram
        histogram = cv2.calcHist([tmp], [0], None, [255], [0, 256])[:, 0]
        histogram = histogram/(histogram.sum() + 1e-6)
       
        # histogram smoothing
        window_size = 9
        kernel      = numpy.ones(window_size) / window_size
        histogram   = numpy.convolve(histogram, kernel, mode='same')

        histogram = numpy.expand_dims(histogram, 1)
    
        return histogram

    def _compute_colorfulness(self, x):
        R, G, B = x[:, :, 0], x[:, :, 1], x[:, :, 2]
        
        rg = numpy.abs(R - G)
        gb = numpy.abs(G - B)
        br = numpy.abs(B - R)

        colorfulness = numpy.sqrt(rg**2 + gb**2 + br**2)
        colorfulness = colorfulness/(2**0.5)
        
        return colorfulness
    
    def _compute_fft(self, x):
        f = numpy.fft.fft2(x)
        f = numpy.fft.fftshift(f)
        y = numpy.log(1.0 + numpy.abs(f))
        y = y/(numpy.max(y) + 10e-6)
        y = numpy.array(y, dtype=numpy.float32)

        return y

    def _normalise_edges(self, x):
        y = 0.5*((x/4.0) + 1.0)
        y = numpy.clip(y, 0.0, 1.0)

        return y
    

if __name__ == "__main__":

    env = PhotoToolBoxEnv()
    state = env.reset()

    print(">>> ", state.shape, state.mean(), state.std(), state.min(), state.max())

    for n in range(10):
        action = numpy.random.randn(env.get_actions_count())
        state, reward, done = env.step(action)
        print(reward, done)

        if done:
            env.reset()