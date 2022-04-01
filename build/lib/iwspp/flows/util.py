from __future__ import division
import datetime
import numpy as np
from PIL import Image
import cv2 as cv
import spams
import matplotlib.pyplot as plt

ADDITIONAL_NP_STATS = False

def pil_to_np_rgb(img):
  """
  Convert a PIL Image to a NumPy array.
  As: RGB PIL (w, h) -> NumPy (h, w, 3).
  """
  return np.asarray(img)

def np_to_pil(np_img):
  """
  Convert a NumPy array to a PIL Image.
  Args:
    np_img: The image represented as a NumPy array.
  Returns:
     The NumPy array converted to a PIL Image.
  """
  if np_img.dtype == "bool":
    np_img = np_img.astype("uint8") * 255
  elif np_img.dtype == "float64":
    np_img = (np_img * 255).astype("uint8")
  return Image.fromarray(np_img)


def np_info(np_arr, name=None, elapsed=None):
  """
  Display information (shape, type, max, min, etc) about a NumPy array.
  Args:
    np_arr: The NumPy array.
    name: The (optional) name of the array.
    elapsed: The (optional) time elapsed to perform a filtering operation.
  """

  if name is None:
    name = "NumPy Array"
  if elapsed is None:
    elapsed = "---"

  if ADDITIONAL_NP_STATS is False:
    print("%-20s | Time: %-14s  Type: %-7s Shape: %s" % (name, str(elapsed), np_arr.dtype, np_arr.shape))
  else:
    # np_arr = np.asarray(np_arr)
    max = np_arr.max()
    min = np_arr.min()
    mean = np_arr.mean()
    is_binary = "T" if (np.unique(np_arr).size == 2) else "F"
    print("%-20s | Time: %-14s Min: %6.2f  Max: %6.2f  Mean: %6.2f  Binary: %s  Type: %-7s Shape: %s" % (
      name, str(elapsed), min, max, mean, is_binary, np_arr.dtype, np_arr.shape))
  return


def display_img(np_img):
  """
  Convert a NumPy array to a PIL image, and display the image.
  Args:
    np_img: Image as a NumPy array.
  """
  result = np_to_pil(np_img)
  if result.mode == 'L':
    result = result.convert('RGB')
  result.show()


def mask_rgb(rgb, mask):
  """
  Apply a binary (T/F, 1/0) mask to a 3-channel RGB image and output the result.
  Args:
    rgb: RGB image as a NumPy array.
    mask: An image mask to determine which pixels in the original image should be displayed.
  """
  return rgb * np.dstack([mask, mask, mask])

class Time:
  """
  Class for displaying elapsed time.
  """

  def __init__(self):
    self.start = datetime.datetime.now()

  def elapsed_display(self):
    time_elapsed = self.elapsed()
    print("Time elapsed: " + str(time_elapsed))

  def elapsed(self):
    self.end = datetime.datetime.now()
    time_elapsed = self.end - self.start
    return time_elapsed



##########################################
## Integrating from github, remove redundancies

def read_image(path):
    """
    Read an image to RGB uint8
    :param path:
    :return:
    """
    im = cv.imread(path)
    im = cv.cvtColor(im, cv.COLOR_BGR2RGB)
    return im


def show_colors(C):
    """
    Shows rows of C as colors (RGB)
    :param C:
    :return:
    """
    n = C.shape[0]
    for i in range(n):
        if C[i].max() > 1.0:
            plt.plot([0, 1], [n - 1 - i, n - 1 - i], c=C[i] / 255, linewidth=20)
        else:
            plt.plot([0, 1], [n - 1 - i, n - 1 - i], c=C[i], linewidth=20)
        plt.axis('off')
        plt.axis([0, 1, -1, n])


def show(image, now=True, fig_size=(10, 10)):
    """
    Show an image (np.array).
    Caution! Rescales image to be in range [0,1].
    :param image:
    :param now:
    :param fig_size:
    :return:
    """
    image = image.astype(np.float32)
    m, M = image.min(), image.max()
    if fig_size != None:
        plt.rcParams['figure.figsize'] = (fig_size[0], fig_size[1])
    plt.imshow((image - m) / (M - m), cmap='gray')
    plt.axis('off')
    if now == True:
        plt.show()


def build_stack(tup):
    """
    Build a stack of images from a tuple of images
    :param tup:
    :return:
    """
    N = len(tup)
    if len(tup[0].shape) == 3:
        h, w, c = tup[0].shape
        stack = np.zeros((N, h, w, c))
    if len(tup[0].shape) == 2:
        h, w = tup[0].shape
        stack = np.zeros((N, h, w))
    for i in range(N):
        stack[i] = tup[i]
    return stack


def patch_grid(ims, width=5, sub_sample=None, rand=False, save_name=None):
    """
    Display a grid of patches
    :param ims:
    :param width:
    :param sub_sample:
    :param rand:
    :return:
    """
    N0 = np.shape(ims)[0]
    if sub_sample == None:
        N = N0
        stack = ims
    elif sub_sample != None and rand == False:
        N = sub_sample
        stack = ims[:N]
    elif sub_sample != None and rand == True:
        N = sub_sample
        idx = np.random.choice(range(N), sub_sample, replace=False)
        stack = ims[idx]
    height = np.ceil(float(N) / width).astype(np.uint16)
    plt.rcParams['figure.figsize'] = (18, (18 / width) * height)
    plt.figure()
    for i in range(N):
        plt.subplot(height, width, i + 1)
        im = stack[i]
        show(im, now=False, fig_size=None)
    if save_name != None:
        plt.savefig(save_name)
    plt.show()

def open_image_np(filename):
  """
  Open an image as an RGB NumPy array.
  (accepted *.jpg, *.png, etc)
  Args:
    filename: Name of the image file.
  returns:
    A NumPy representing an RGB image.
  """
  image = Image.open(filename)
  return pil_to_np_rgb(image)

######################################

def standardize_brightness(I):
    """

    :param I:
    :return:
    """
    p = np.percentile(I, 90)
    return np.clip(I * 255.0 / p, 0, 255).astype(np.uint8)


def remove_zeros(I):
    """
    Remove zeros, replace with 1's.
    :param I: uint8 array
    :return:
    """
    mask = (I == 0)
    I[mask] = 1
    return I


def RGB_to_OD(I):
    """
    Convert from RGB to optical density
    :param I:
    :return:
    """
    I = remove_zeros(I)
    return -1 * np.log(I / 255)


def OD_to_RGB(OD):
    """
    Convert from optical density to RGB
    :param OD:
    :return:
    """
    return (255 * np.exp(-1 * OD)).astype(np.uint8)


def normalize_rows(A):
    """
    Normalize rows of an array
    :param A:
    :return:
    """
    return A / np.linalg.norm(A, axis=1)[:, None]


def notwhite_mask(I, thresh=0.8):
    """
    Get a binary mask where true denotes 'not white'
    :param I:
    :param thresh:
    :return:
    """
    I_LAB = cv.cvtColor(I, cv.COLOR_RGB2LAB)
    L = I_LAB[:, :, 0] / 255.0
    return (L < thresh)


def sign(x):
    """
    Returns the sign of x
    :param x:
    :return:
    """
    if x > 0:
        return +1
    elif x < 0:
        return -1
    elif x == 0:
        return 0


def get_concentrations(I, stain_matrix, lamda=0.01):
    """
    Get concentrations, a npix x 2 matrix
    :param I:
    :param stain_matrix: a 2x3 stain matrix
    :return:
    """
    OD = RGB_to_OD(I).reshape((-1, 3))
    return spams.lasso(OD.T, D=stain_matrix.T, mode=2, lambda1=lamda, pos=True).toarray().T

