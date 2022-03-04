import numpy as np
import pandas as pd
import os
import skimage.color as sk_color
from iwspp.flows import util, slide


def filter_grays(np_img, tolerance=15, output_type="bool"):
  """
  Create a mask to filter out pixels where the red, green, and blue channel values are similar.
  Args:
    np_img: RGB image as a NumPy array.
    tolerance: Tolerance value to determine how similar the values must be in order to be filtered out
    output_type: Type of array to return (bool, float, or uint8).
  Returns:
    NumPy array representing a mask where pixels with similar red, green, and blue values have been masked out.
  """
  t = util.Time()
  (h, w, c) = np_img.shape

  rgb = np_img.astype(np.int)
  rg_diff = abs(rgb[:, :, 0] - rgb[:, :, 1]) <= tolerance
  rb_diff = abs(rgb[:, :, 0] - rgb[:, :, 2]) <= tolerance
  gb_diff = abs(rgb[:, :, 1] - rgb[:, :, 2]) <= tolerance
  result = ~(rg_diff & rb_diff & gb_diff)

  if output_type == "bool":
    pass
  elif output_type == "float":
    result = float(result)
    # result = result.astype(float)
  else:
    result = int(result)
    #result = result.astype("uint8") * 255
  util.np_info(result, "Filter Grays", t.elapsed())
  return result


def mask_percent(np_img):
  """
  Determine the percentage of a NumPy array that is masked (how many of the values are 0 values).
  Args:
    np_img: Image as a NumPy array.
  Returns:
    The percentage of the NumPy array that is masked.
  """
  if (len(np_img.shape) == 3) and (np_img.shape[2] == 3):
    np_sum = np_img[:, :, 0] + np_img[:, :, 1] + np_img[:, :, 2]
    mask_percentage = 100 - np.count_nonzero(np_sum) / np_sum.size * 100
  else:
    mask_percentage = 100 - np.count_nonzero(np_img) / np_img.size * 100
  return mask_percentage


def apply_image_filters(path, fps):
  """
  Apply filters to image as NumPy array and save.
  Args:
    path: Path to images derived from slides.
    fps:  The new path to save the masked image
  Returns:
    Mask percentage
  """
  img = slide.open_image(path)
  rgb = util.pil_to_np_rgb(img)
  mask_not_gray = filter_grays(rgb)
  rgb_not_gray = util.mask_rgb(rgb, mask_not_gray)

  mask_percentage = mask_percent(rgb_not_gray)
  pil_img = util.np_to_pil(rgb_not_gray)

  pil_img.save(fps)
  return mask_percentage


def tissue_percent(np_img):
  """
  Determine the percentage of a NumPy array that is tissue (not masked).
  Args:
    np_img: Image as a NumPy array.
  Returns:
    The percentage of the NumPy array that is tissue.
  """
  return 100 - mask_percent(np_img)


def filter_rgb_to_hsv(np_img, display_np_info=True):
  """
  Filter RGB channels to HSV (Hue, Saturation, Value).
  Args:
    np_img: RGB image as a NumPy array.
    display_np_info: If True, display NumPy array info and filter time.
  Returns:
    Image as NumPy array in HSV representation.
  """

  if display_np_info:
    t = util.Time()
  hsv = sk_color.rgb2hsv(np_img)
  if display_np_info:
    util.np_info(hsv, "RGB to HSV", t.elapsed())
  return hsv


def filter_hsv_to_h(hsv, output_type="int", display_np_info=True):
  """
  Obtain hue values from HSV NumPy array as a 1-dimensional array.
  If output as an int array, the original float
  values are multiplied by 360 for their degree equivalents for simplicity.
  For more information, see
  https://en.wikipedia.org/wiki/HSL_and_HSV
  Args:
    hsv: HSV image as a NumPy array.
    output_type: Type of array to return (float or int).
    display_np_info: If True, display NumPy array info and filter time.
  Returns:
    Hue values (float or int) as a 1-dimensional NumPy array.
  """
  if display_np_info:
    t = util.Time()
  h = hsv[:, :, 0]
  h = h.flatten()
  if output_type == "int":
    h *= 360
    h = h.astype("int")
  if display_np_info:
    util.np_info(hsv, "HSV to H", t.elapsed())
  return h


def filter_hsv_to_s(hsv):
  """
  Experimental HSV to S (saturation).
  Args:
    hsv:  HSV image as a NumPy array.
  Returns:
    Saturation values as a 1-dimensional NumPy array.
  """
  s = hsv[:, :, 1]
  s = s.flatten()
  return s


def filter_hsv_to_v(hsv):
  """
  Experimental HSV to V (value).
  Args:
    hsv:  HSV image as a NumPy array.
  Returns:
    Value values as a 1-dimensional NumPy array.
  """
  v = hsv[:, :, 2]
  v = v.flatten()
  return v


def multi_apply_filters_to_images(path, sl_format):
  """
  Apply a set of filters to image folder
  Args:
    path: The image folder.
    sl_format: The file format of the images.
  Returns:
    Tuple of 1) Dictionary of mask percentage and path to filtered images
  """

  timer = util.Time()
  info = dict()
  n_path = os.path.join(path, "filtered")
  print(n_path)

  files = [f for f in os.listdir(path) if f.endswith(sl_format)]
  print("Applying filters to {} image".format(len(files)))

  if not os.path.exists(n_path):
    os.makedirs(n_path)

  for key, i in enumerate(files):
    sl = os.path.join(path, i)
    fps = os.path.join(n_path, i)
    mask_per = apply_image_filters(sl, fps)
    info[key] = sl + "_" + fps + "==" + str(mask_per)

  info = pd.DataFrame(list(info.items()), columns=["key", "Mask"])
  info.to_csv(os.path.join(n_path, "Mask_percent.csv"), index=False)

  timer.elapsed_display()
  return

