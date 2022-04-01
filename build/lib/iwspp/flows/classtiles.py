"""
Name: slide
Author: Chinedu A. Anene, Phd
"""

import image_slicer
import os
import copy
import pandas as pd
from PIL import ImageOps, ImageDraw
from iwspp.flows import util, stain, filter
from PIL import Image
from iwspp.flows.util import Time




class Tile:
  """
  Class for handling image tiles.
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
