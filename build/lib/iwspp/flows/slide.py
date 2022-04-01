"""
Name: slide
Author: Chinedu A. Anene, Phd
"""

import os
import sys
import math
import openslide as op
import numpy as np
from openslide.deepzoom import DeepZoomGenerator
import PIL
from iwspp.flows import util, filter, stain
from iwspp.flows.util import Time


class Slide:
  """
  Class for handling slides.
  """

  def __init__(self, x, f="slide"):
      """
      Slide class.

      Parameters:
          x: Input file name (slide or image).
          f: Type of the input file specified by x (slide or image).
      """
      self.x = x
      self.f = f
      self.__loaded = 0
      self.__slide = None
      self.__image = None
      self.__scaled = None
      self.__save_n = None
      self.__scores = []

  def __str__(self):
      return "Slide class for holding and processing slides."

  def __repr__(self):
      return "\n" + self.__str__()

  def __open(self):
      """
      Get file specified by x into the class (accept various formats).
            slide = .svs, etc
            image = .jpg, .png, etc
      """
      dr_name = os.path.dirname(self.x)
      sl_name = os.path.basename(self.x)[:-4]
      self.__save_n = os.path.join(dr_name, "converted", sl_name)

      if not os.path.exists(self.__save_n):
          os.makedirs(self.__save_n)

      if self.f == "slide":
          try:
              self.__slide = op.open_slide(self.x)
              self.__loaded = 1

          except op.OpenSlideError:
              print("ERROR: OpenSlide failed to open the slide.")

          except FileNotFoundError:
              print("ERROR: File is not found in the CWD.")

      elif self.f == "image":
          try:
              self.__image = PIL.Image.open(self.x)
              self.__loaded = 1

          except FileNotFoundError:
              print("ERROR: File is not found in the CWD.")

      else:
          print("ERROR: The f arguments is not recognised, needs slide or image")

      return

  def info(self):
      """
      Display various properties about the loaded slide.
      """
      if self.__loaded == 1:
          if self.f == "slide":
              print("Level count: {}".format(self.__slide.level_count))
              print("Level dimensions: {}".format(self.__slide.level_dimensions))
              print("Level downsamples: {}".format(self.__slide.level_downsamples))
              print("Dimensions: {}".format(self.__slide.dimensions))
              print("Objective power: {}".format(self.__slide.properties[op.PROPERTY_NAME_OBJECTIVE_POWER]))

          else:
              print("Dimensions: {}".format(self.__image.size))
              print("Mode : {}".format(self.__image.mode))

      else:
          print("ERROR: Slide or image is not loaded yet.")

      return


  def __slide2image(self, s=32):
      """
      Convert OpenSlide object to a scaled image.
      Args:
        s: Scaling factor (8, 16, 32, 64)
      Returns:
        [original: width - height, new: width - height].
      """

      if self.__slide is None and self.__image is None:
          print("ERROR: Slide and image object is not loaded yet.")

      else:
          if self.__image is None:
              o_w, o_h = self.__slide.dimensions
              n_w, n_h = math.floor(o_w / s), math.floor(o_h / s)
              le = self.__slide.get_best_level_for_downsample(s)
              wsi = self.__slide.read_region((0, 0), le, self.__slide.level_dimensions[le])

              wsi = wsi.convert("RGB")
              s2i = wsi.resize((n_w, n_h), PIL.Image.BILINEAR)

          else:
              o_w, o_h = self.__image.size
              n_w, n_h = math.floor(o_w / s), math.floor(o_h / s)

              s2i = self.__image.resize((n_w, n_h), PIL.Image.BILINEAR)

          s2n = util.pil_to_np_rgb(s2i)
          self.__scaled = {"image": s2i, "np_image": s2n,
                       "old_w": o_w, "old_h": o_h,
                       "new_w": n_w, "new_h": n_h}

      return


  def __get_zoom(self, t=300, mx=10, threshold=90, sample=0.5, n=50):
      """
      Convert OpenSlide object to a scaled image.
      See fit() for the arguments.
      Note that this function need to default at some n number to avoid waste.

      """



      # Highest zoom
      hzl = op.deepzoom.DeepZoomGenerator(self.__slide, t, overlap=0)
      gen_hz = hzl.level_count - 1

      try:
          mag = int(self.__slide.properties[op.PROPERTY_NAME_OBJECTIVE_POWER])
          offset = math.floor((mag / mx) / 2)
          level = hzl.level_count - offset

      except ValueError:
          level = gen_hz

      except KeyError:
          level = gen_hz


      # Tiles at zoom level
      try:
          cols, rows = hzl.level_tiles[level]

      except IndexError:
          print("ERROR : mx argument is larger than the maximum mag for slide")
          sys.exit("Try again")


      index = [(c, r) for c in range(cols) for r in range(rows)]
      mms = n

      for i in range(len(index)):
          if mms != 0:
              s2n = hzl.get_tile(level, index[i])

              if s2n.size[0] == t and s2n.size[1] == t:
                  np_img = util.pil_to_np_rgb(s2n)
                  mask_not_gray = filter.filter_grays(np_img)
                  rgb_not_gray = util.mask_rgb(np_img, mask_not_gray)
                  tp = filter.tissue_percent(rgb_not_gray)

                  if tp >= threshold:
                      sp = np.random.choice((1, 0), p=[sample, 1 - sample])

                      if sp == 1:
                          mms -= 1
                          score, _, _, qun_factor = stain.score_tile(np_img, tp)

                          f_n = (os.path.basename(self.x) + "_slice_0" + str(index[i][0])
                                 + "_0" + str(index[i][1]) + ".jpg")

                          self.__scores.append((score, qun_factor))
                          s2n.save(os.path.join(self.__save_n, f_n), "JPEG")

          else:
              print("ALERT: iwspp got the requested {} tiles".format(n))
              break

      return


  def show(self):
      """
      Show scaled image on screen.
      """
      if self.__scaled is None:
          print("ERROR: Please, fit the class first before using this code.")

      else:
          self.__scaled["image"].show()
      return

  def fit(self, s=32, t=300, mx=5, threshold=85, sample=0.4, n=20):
      """
      Fit the class.
      Args:
          s: Scaling factor.
          t: Size of the tiles.
          mx: The desired magnification level.
          threshold: Tissue percentage threshold.
          sample: Probability of sampling s valid tile (0-1).
          n: Maximum number of tiles to get per slide.
      """
      self.__open()
      self.__slide2image(s)
      self.__get_zoom(t=t, mx=mx,
                      threshold=threshold,
                      sample=sample, n=n)
      """
      Note : get_zoom(), makes key assumptions for performance optimisation.
      """
      return

  def save(self, path):
      """
      Save the converted image and meta data to file.

      Args:
        path: The path to save the image.
      """
      print("Saving to {}".format(path))
      self.__scaled["image"].save(path, "JPEG")
      return


def multi_slide_to_image(path, tf=".svs", f="slide", s=64, t=300,
                         mx=5, threshold=90, sample=0.5, n=200):
  """
  Convert multiple slides to images from a folder to "converted" folder.

  Args:
        path: The path to save the image
        tf: Universal file extension for target folder
        f: Indicate if image or slide was loaded
        s: Scaling factor
        t: Size of the tiles
        mx: The desired magnification level
        threshold: Tissue percentage threshold
        sample: Probability of sampling s valid tile (0-1)
        n: Maximum number of tiles to get per slide

  """
  timer = Time()

  n_path = os.path.join(path, "converted")
  if not os.path.exists(n_path):
      os.makedirs(n_path)
      print("ATTENTION: Converted files are in {}".format(n_path))

  files = os.listdir(path)

  for i in files:
      if i.endswith(tf):
          print(i)
          sl = Slide(x=str(os.path.join(path, i)), f=f)
          sl.fit(s=s, t=t, mx=mx, threshold=threshold, sample=sample, n=n)
          # sl.info()
          fps = os.path.join(n_path, i[:-4], (i + ".jpg"))
          sl.save(fps)

  timer.elapsed_display()
  return


# multi_slide_to_image("data/", tf=".svs", f="slide", s=32, mx=6, threshold=90)
