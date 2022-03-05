"""
Name: slide
Author: Chinedu A. Anene, Phd
"""

import os
import math
import openslide as op
import PIL
from iwspp.flows import util
from iwspp.flows.util import Time


class Slide:
  """
  Class for handling slide files.
  """

  def __init__(self, x, f = "slide"):
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

              # Convert to RGB
              wsi = wsi.convert("RGB")

              # Convert to PIL image
              s2i = wsi.resize((n_w, n_h), PIL.Image.BILINEAR)

          else:
              o_w, o_h = self.__image.size
              n_w, n_h = math.floor(o_w / s), math.floor(o_h / s)

              s2i = self.__image.resize((n_w, n_h), PIL.Image.BILINEAR)

          # Convert to numpy array
          s2n = util.pil_to_np_rgb(s2i)

          # Global Save things
          self.__scaled = {"image": s2i, "np_image": s2n,
                       "old_w": o_w, "old_h": o_h,
                       "new_w": n_w, "new_h": n_h}

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

  def fit(self, s=32):
      """
      Fit the class.
      Args:
          s: Scaling factor
      """
      self.__open()
      self.__slide2image(s)
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


def multi_slide_to_image(path, tf=".svs", f="slide", s=32):
  """
  Convert multiple slides to images from a folder to "converted" folder.

  Args:
        path: The path to save the image
        tf: Universal file extension for target folder
        f: Type of data been loaded (for extension)
        s: Scaling factor
  """
  timer = Time()

  n_path = os.path.join(path, "converted")
  if not os.path.exists(n_path):
      os.makedirs(n_path)
      print("ATTENTION: Converted files are in {}".format(n_path))

  files = os.listdir(path)

  for i in files:
      if i.endswith(tf):
          sl = Slide(x=str(os.path.join(path, i)), f=f)
          sl.fit(s=s)
          sl.info()

          # Prepare the path and save
          fps = os.path.join(n_path, (i + ".jpg"))
          sl.save(fps)

  timer.elapsed_display()
  return


# Test it
# multi_slide_to_image("Data/", tf=".svs", f="slide", s=16)