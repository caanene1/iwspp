import image_slicer
import os
import copy
import pandas as pd
from PIL import ImageOps, ImageDraw
from iwspp.flows import util, stain, filter
from iwspp.flows.slide import open_image
from iwspp.flows.util import Time


def get_num_tiles(path):
  """
  N tiles proportional to image size.
  Args:
    path: Image full path.
  Returns:
    N tiles.
  """

  r_si, c_si = open_image(path).size

  r_t_si = r_si * 10 // 1041
  c_t_si = c_si * 10 // 1041

  n =  r_t_si * c_t_si

  if n < 2:
      n = 2
  return int(n)

def get_tiles_score_save(path, save_path, save_all=False, tp_threshold=80):
    """
    Obtain tissue rich slicers.
    Score and create annotation tiles.
    Args:
      path: Image path.
      save_path: Save to.
      save_all: Optional slices (not recommended).
      tp_threshold: Minimum tissue content.
    Returns:
      Save tiles and annotation.
    """

    base_n = os.path.basename(path[:-4])
    n_path = os.path.join(save_path, base_n, "selectedTiles")
    n_path2 = os.path.join(save_path, base_n, "allTiles")

    if not os.path.exists(n_path):
        os.makedirs(n_path)

    tiles = image_slicer.slice(path, get_num_tiles(path), save=False)
    s_tiles = list(copy.deepcopy(tiles))


    l_tiles = list()
    tile_name = []
    s_score = []
    s_color_factor = []
    s_s_and_v_factor = []
    s_quantity_factor = []

    if save_all:
        if not os.path.exists(n_path2):
            os.makedirs(n_path2)
        image_slicer.save_tiles(tiles, directory=n_path2,
                                prefix=b_name + "_slice", format="JPEG")

    for i in range(len(tiles)):
        t_n = "0" + str(tiles[i].column) + "_0" + str(tiles[i].row)
        pil_img = tiles[i].image
        np_img = util.pil_to_np_rgb(pil_img)
        tp = filter.tissue_percent(np_img)

        if tp >= tp_threshold:
            l_tiles.append(tiles[i])

            # Score
            score, color_factor, s_and_v_factor, quantity_factor = stain.score_tile(np_img, tp)
            tile_name.append(base_n + "_slice_0" + str(tiles[i].column) + "_0" + str(tiles[i].row) + ".jpg")
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
    s_tiles = image_slicer.join(s_tiles)
    s_tiles = s_tiles.convert("RGB")
    s_tiles.save(fp=os.path.join(n_path, "annotation.jpg"))

    # Table
    stats_s_tiles = pd.DataFrame()
    stats_s_tiles["Name"] = tile_name
    stats_s_tiles["score"] = s_score
    stats_s_tiles["color_factor"] = s_color_factor
    stats_s_tiles["s_and_v_factor"] = s_s_and_v_factor
    stats_s_tiles["quantity_factor"] = s_quantity_factor
    stats_s_tiles["source"] = base_n

    stats_s_tiles.to_csv(os.path.join(n_path, "annotation.csv"), index=False)

    # Save
    image_slicer.save_tiles(l_tiles, directory=n_path,
                            prefix=b_name + "_slice", format="JPEG")
    return

def multi_get_tiles_score_save(path, sl_format, tp_threshold=80):
    """
    Apply a set of filters to image folder

    :param path: Image folder.
    :param sl_format: The file format of the images.
    :param tp_threshold: The percentage tissue quantity to retain.
    :return:
    Tiles to folder
    """
    timer = Time()

    files = os.listdir(path)
    new_path = os.path.join(path, "tiles")

    if not os.path.isdir(new_path):
        os.mkdir(new_path)
        os.chdir(os.path.join(os.getcwd(), new_path))

    print("Tilling {} images".format(len(files)))

    save_it = os.getcwd()
    for i in files:
        if i.endswith(sl_format):
            sl = str(os.path.join(path, i))
            get_tiles_score_save(sl, save_it, tp_threshold=tp_threshold)
    timer.elapsed_display()
    return path




