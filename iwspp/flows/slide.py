import math
import openslide
from openslide import OpenSlideError
import os
import PIL
from PIL import Image
from iwspp.flows import util
from iwspp.flows.util import Time


def open_slide(fn):
  """
  Open a pathology slide (*.svs, etc).
  Args:
    fn: file name to load.
  Returns:
    OpenSlide whole-slide object.
    Indicates if slides was loaded or not.
  """
  try:
    slide = openslide.open_slide(fn)
  except OpenSlideError:
    slide = None
  except FileNotFoundError:
    slide = None
  return slide


def open_image(im):
  """
  Open an image (*.jpg, *.png, etc).
  Args:
    im: Image name/path.
  returns:
    A pil image.
  """
  image = Image.open(im)
  return image


def slide_to_image(sl, path, s=64):
  """
  Convert slide image to jpg or png.
  Args:
    sl: The slide
    path: The path to save the converted image
    s: Scaling factor
  """
  img, o_w, o_h, n_w, n_h = slide_to_scaled_pil(sl, s)
  print("Saving to {}".format(path))
  img.save(path, "JPEG")
  return


def slide_to_scaled_pil(s_obj, s=64):
  """
  Convert OpenSlide object to a scaled PIL image.
  Args:
    s_obj: Slide.
    s: Scaling factor
  Returns:
    Tuple of PIL image, [original: width - height, new: width - height].
  """
  print("Opening Slide {}".format(s_obj))
  o_w, o_h = s_obj.dimensions

  if s is None:
    scale = 32
  else:
    scale = s
  n_w, n_h = math.floor(o_w / scale), math.floor(o_h / scale)
  level = s_obj.get_best_level_for_downsample(scale)
  w_s_i = s_obj.read_region((0, 0), level, s_obj.level_dimensions[level])
  w_s_i = w_s_i.convert("RGB")
  img = w_s_i.resize((n_w, n_h), PIL.Image.BILINEAR)
  return img, o_w, o_h, n_w, n_h


def slide_to_scaled_np_image(sl):
  """
  Convert slide to a scaled NumPy.
  Args:
    sl: The slide.
  Returns:
    Tuple consisting of scaled-down NumPy image, original width,
    original height, new width, and new height.
  """
  img, o_w, o_h, n_w, n_h = slide_to_scaled_pil(sl)
  np_img = util.pil_to_np_rgb(img)
  return np_img, o_w, o_h, n_w, n_h


def show_slide(sl, s):
  """
  Show pathology slide on screen, with PIL and scaled.
  Args:
    sl: Open slide object.
    s: scaling factor
  """
  pil_img = slide_to_scaled_pil(sl, s)[0]
  pil_img.show()
  return


def slide_info(s_obj):
  """
  Display information (such as properties) about slide.
  Args:
    Print properties
  """
  print("Level count: {}".format(s_obj.level_count))
  print("Level dimensions: {}".format(s_obj.level_dimensions))
  print("Level downsamples: {}".format(s_obj.level_downsamples))
  print("Dimensions: {}".format(s_obj.dimensions))
  print("Objective power: {}".format(s_obj.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER]))
  return


def multi_slides_to_images(path, sl_format, s=64):
  """
  Convert slides to images from folder to folder.
  Control the images with "sl_format"
  """
  timer = Time()

  n_path = os.path.join(path, "converted")
  if not os.path.exists(n_path):
    os.makedirs(n_path)

  files = os.listdir(path)

  for i in files:
    if i.endswith(sl_format):
      sl = open_slide(str(os.path.join(path, i)))
      fps = os.path.join(n_path, (i + ".jpg"))
      slide_to_image(sl, fps, s=s)
  timer.elapsed_display()
  return


def open_image_np(filename):
  """
  Open an image (*.jpg, *.png, etc) as an RGB NumPy array.
  Args:
    filename: Name of the image file.
  returns:
    A NumPy representing an RGB image.
  """
  pil_img = open_image(filename)
  np_img = util.pil_to_np_rgb(pil_img)
  return np_img
