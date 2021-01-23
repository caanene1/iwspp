import numpy as np
from enum import Enum
from SRC import filter
###### Credit to https://github.com/deroneriksson/python-wsi-preprocessing/tree/master/deephistopath/wsi

# Constant
HSV_PURPLE = 270
HSV_PINK = 330
TISSUE_HIGH_THRESH = 80
TISSUE_LOW_THRESH = 10

# F1
def rgb_to_hues(rgb):
  """
  Convert RGB NumPy array to 1-dimensional array of hue values (HSV H values in degrees).
  Args:
    rgb: RGB image as a NumPy array
  Returns:
    1-dimensional array of hue values in degrees
  """
  hsv = filter.filter_rgb_to_hsv(rgb, display_np_info=False)
  h = filter.filter_hsv_to_h(hsv, display_np_info=False)
  return h
# F2
def hsv_purple_deviation(hsv_hues):
  """
  Obtain the deviation from the HSV hue for purple.
  Args:
    hsv_hues: NumPy array of HSV hue values.
  Returns:
    The HSV purple deviation.
  """
  purple_deviation = np.sqrt(np.mean(np.abs(hsv_hues - HSV_PURPLE) ** 2))
  return purple_deviation
# F3
def hsv_pink_deviation(hsv_hues):
  """
  Obtain the deviation from the HSV hue for pink.
  Args:
    hsv_hues: NumPy array of HSV hue values.
  Returns:
    The HSV pink deviation.
  """
  pink_deviation = np.sqrt(np.mean(np.abs(hsv_hues - HSV_PINK) ** 2))
  return pink_deviation
# F4
def hsv_purple_pink_factor(rgb):
  """
  Compute scoring factor based on purple and pink HSV hue deviations and degree to which a narrowed hue color range
  average is purple versus pink.
  Args:
    rgb: Image an NumPy array.
  Returns:
    Factor that favors purple (hematoxylin stained) tissue over pink (eosin stained) tissue.
  """
  hues = rgb_to_hues(rgb)
  hues = hues[hues >= 260]  # exclude hues under 260
  hues = hues[hues <= 340]  # exclude hues over 340
  if len(hues) == 0:
    return 0  # if no hues between 260 and 340, then not purple or pink
  pu_dev = hsv_purple_deviation(hues)
  pi_dev = hsv_pink_deviation(hues)
  avg_factor = (340 - np.average(hues)) ** 2

  if pu_dev == 0:  # avoid divide by zero if tile has no tissue
    return 0

  factor = pi_dev / pu_dev * avg_factor
  return factor
# F5
def hsv_saturation_and_value_factor(rgb):
  """
  Function to reduce scores of tiles with narrow HSV saturations and values since saturation and value standard
  deviations should be relatively broad if the tile contains significant tissue.
  Example of a blurred tile that should not be ranked as a top tile:
    ../data/tiles_png/006/TUPAC-TR-006-tile-r58-c3-x2048-y58369-w1024-h1024.png
  Args:
    rgb: RGB image as a NumPy array
  Returns:
    Saturation and value factor, where 1 is no effect and less than 1 means the standard deviations of saturation and
    value are relatively small.
  """
  hsv = filter.filter_rgb_to_hsv(rgb, display_np_info=False)
  s = filter.filter_hsv_to_s(hsv)
  v = filter.filter_hsv_to_v(hsv)
  s_std = np.std(s)
  v_std = np.std(v)
  if s_std < 0.05 and v_std < 0.05:
    factor = 0.4
  elif s_std < 0.05:
    factor = 0.7
  elif v_std < 0.05:
    factor = 0.7
  else:
    factor = 1

  factor = factor ** 2
  return factor
# C1
class TissueQuantity(Enum):
  NONE = 0
  LOW = 1
  MEDIUM = 2
  HIGH = 3

# F6
def tissue_quantity(tissue_percentage):
  """
  Obtain TissueQuantity enum member (HIGH, MEDIUM, LOW, or NONE) for corresponding tissue percentage.
  Args:
    tissue_percentage: The tile tissue percentage.
  Returns:
    TissueQuantity enum member (HIGH, MEDIUM, LOW, or NONE).
  """
  if tissue_percentage >= TISSUE_HIGH_THRESH:
    return TissueQuantity.HIGH
  elif (tissue_percentage >= TISSUE_LOW_THRESH) and (tissue_percentage < TISSUE_HIGH_THRESH):
    return TissueQuantity.MEDIUM
  elif (tissue_percentage > 0) and (tissue_percentage < TISSUE_LOW_THRESH):
    return TissueQuantity.LOW
  else:
    return TissueQuantity.NONE
# F7
def tissue_quantity_factor(amount):
  """
  Obtain a scoring factor based on the quantity of tissue in a tile.
  Args:
    amount: Tissue amount as a TissueQuantity enum value.
  Returns:
    Scoring factor based on the tile tissue quantity.
  """
  if amount == TissueQuantity.HIGH:
    quantity_factor = 1.0
  elif amount == TissueQuantity.MEDIUM:
    quantity_factor = 0.2
  elif amount == TissueQuantity.LOW:
    quantity_factor = 0.1
  else:
    quantity_factor = 0.0
  return quantity_factor
# F8
def score_tile(np_tile, tissue_percent):
  """
  Score tile based on tissue percentage, color factor, saturation/value factor, and tissue quantity factor.
  Args:
    np_tile: Tile as NumPy array.
    tissue_percent: The percentage of the tile judged to be tissue.
  Returns tuple consisting of score, color factor, saturation/value factor, and tissue quantity factor.
  """
  color_factor = hsv_purple_pink_factor(np_tile)
  s_and_v_factor = hsv_saturation_and_value_factor(np_tile)
  amount = tissue_quantity(tissue_percent)
  quantity_factor = tissue_quantity_factor(amount)
  combined_factor = color_factor * s_and_v_factor * quantity_factor
  score = (tissue_percent ** 2) * np.log(1 + combined_factor) / 1000.0
  # scale score to between 0 and 1
  score = 1.0 - (10.0 / (10.0 + score))
  return score, color_factor, s_and_v_factor, quantity_factor
