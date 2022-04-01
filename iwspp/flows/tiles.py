"""
Name: slide
Author: Chinedu A. Anene, Phd
"""

import image_slicer as ims
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
  Note: Expects images (JPEG, PNG, etc)
  """

  def __init__(self, x, o, t=80, sa=False):
      """
      Slide class.

      Parameters:
          x: Input file path (image)
          o: Output path
          t: Content threshold
          sa: Save all tiles (not recommended)
      """
      self.x = x
      self.o = o
      self.t = t
      self.sa = sa
      self.__loaded = 0
      self.__tile = None
      self.__image = None
      self.__bn = os.path.basename(x[:-4])
      self.__np = os.path.join(o, self.__bn, "selectedTile")
      self.__np2 = os.path.join(o, self.__bn, "allTile")
      self.__tab_out = pd.DataFrame()

  def __str__(self):
      return "Slide class for holding and processing slides."

  def __repr__(self):
      return "\n" + self.__str__()


  def __open(self):
      """
      Get image and the associated tiles.
      Note : N is proportional to the image size
      """

      if not os.path.exists(self.__np):
          os.makedirs(self.__np)

      try:
          rs, cs = Image.open(self.x).size
          rts = rs * 10 // 1041
          cts = cs * 10 // 1041
          self.__tile = int(rts * cts)

      except FileNotFoundError:
          print("Ensure you give the full path of the folder.")

      if self.__tile < 2:
          self.__tile = 2

      self.__image = ims.slice(self.x, self.__tile, save=False)

      self.__loaded = 1
      return


  def __gettile(self):
      """
      Obtain content rich slices and create annotation tile.

      """

      s_tiles = list(copy.deepcopy(self.__image))

      l_tiles = list()
      tile_name = []
      s_score = []
      s_color_factor = []
      s_s_and_v_factor = []
      s_quantity_factor = []

      if self.sa:
          # Save everything no checks
          if not os.path.exists(self.__np2):
              os.makedirs(self.__np2)
          ims.save_tiles(self.__image, directory=self.__np2,
                         prefix=self.__bn + "_slice", format="JPEG")

      for i in range(len(self.__image)):
          t_n = "0" + str(self.__image[i].column) + "_0" + str(self.__image[i].row)
          pil_img = self.__image[i].image
          np_img = util.pil_to_np_rgb(pil_img)
          tp = filter.tissue_percent(np_img)

          if tp >= self.t:
              l_tiles.append(self.__image[i])

              # Score
              score, color_factor, s_and_v_factor, quantity_factor = stain.score_tile(np_img, tp)
              tile_name.append(self.__bn + "_slice_0" + str(self.__image[i].column) + "_0"
                               + str(self.__image[i].row) + ".jpg")

              s_score.append(score)
              s_color_factor.append(color_factor)
              s_s_and_v_factor.append(s_and_v_factor)
              s_quantity_factor.append(quantity_factor)

              # Annotate
              pil_img_exp = ImageOps.expand(pil_img, border=2, fill="green")
              draw = ImageDraw.Draw(pil_img_exp)
              draw.text((0, 0), t_n, fill="green")
              s_tiles[i].image = pil_img_exp

          else:
              pil_img_exp = ImageOps.expand(pil_img, border=2, fill="white")
              draw = ImageDraw.Draw(pil_img_exp)
              draw.text((0, 0), t_n, fill="white")
              s_tiles[i].image = pil_img_exp

      # Join
      s_tiles = ims.join(s_tiles)
      s_tiles = s_tiles.convert("RGB")
      s_tiles.save(fp=os.path.join(self.__np, "annotation.jpg"))

      # Table
      self.__tab_out["Name"] = tile_name
      self.__tab_out["score"] = s_score
      self.__tab_out["color_factor"] = s_color_factor
      self.__tab_out["s_and_v_factor"] = s_s_and_v_factor
      self.__tab_out["quantity_factor"] = s_quantity_factor
      self.__tab_out["source"] = self.__np

      self.__tab_out.to_csv(os.path.join(self.__np, "annotation.csv"), index=False)

      # Save
      ims.save_tiles(l_tiles, directory=self.__np,
                              prefix=self.__bn + "_slice", format="JPEG")
      return



  def fit(self):
      """
      Fit the class.
      """
      print("Processing {}".format(self.__bn))
      self.__open()
      self.__gettile()
      return


def multi_image_to_tile(path, sf=".png", threshold=80, sa=False):
    """
    Apply a set of filters to image folder

    Args:
        path: Image folder
        sf: The file format of the images
        threshold: The percentage tissue quantity to retain
        sa: Save all tiles

    """
    timer = Time()

    files = os.listdir(path)
    new_path = os.path.join(path, "tiles")

    if not os.path.isdir(new_path):
        os.mkdir(new_path)
        os.chdir(os.path.join(os.getcwd(), new_path))

    print("Processing {} images".format(len(files)))

    for i in files:
        if i.endswith(sf):
            sl = str(os.path.join(path, i))
            img = Tile(x=sl, o=os.getcwd(), t=threshold, sa=sa)
            img.fit()
    timer.elapsed_display()
    return path

# Enforce specific dimension for the tiles
# multi_image_to_tile(path="/Users/chineduanene/Documents/GitHub/iwspp/data")
