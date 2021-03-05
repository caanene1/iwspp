import image_slicer
import os
import copy
import pandas as pd
from PIL import ImageOps, ImageDraw
from iwspp.flows import util, stain, slide, filter
from iwspp.flows.util import Time


def get_num_tiles(path):
  """
  Obtain the number of tiles that an image can be divided proportional to its dimension.
  Args:
    path: The path to the image.
  Returns:
    Total number of tiles (integer).
  """
  row_size, col_size = slide.open_image(path).size
  # Using 1041 by 940 as base set to 100
  row_tile_size = round(row_size * 10 / 1041)
  col_tile_size = round(col_size * 10 / 1041)
  n_tiles =  row_tile_size * col_tile_size
  return int(n_tiles)


def get_tiles_score_save(path, save_all=False, tp_threshold=80):
    """
    Obtain tissue rich slicers from the filtered images based on tissue percentage.
    Score the tiles and create annotation tiles for mapping back the tiles, re pathologist.
    Args:
      path: The path to the image.
      save_all: Optional True save all image slices (not recommended).
      tp_threshold: Minimum tissue percentage to retain a slice.
    Returns:
      Saves selected tiles or optional all slides.
    """
    n_path = path[:-3] + "selectedTiles"
    n_path2 = path[:-3] + "allTiles"
    # Make directory
    if not os.path.exists(n_path):
        os.makedirs(n_path)
    #
    tiles = image_slicer.slice(path, get_num_tiles(path), save=False)
    s_tiles = list(copy.deepcopy(tiles))

    ## Set variables to populate
    l_tiles = list()
    tile_name = []
    s_score = []
    s_color_factor = []
    s_s_and_v_factor = []
    s_quantity_factor = []
    #
    if save_all:
        if not os.path.exists(n_path2):
            os.makedirs(n_path2)
        image_slicer.save_tiles(tiles, directory=n_path2,
                                prefix="slice", format="JPEG")

    ## Identify tissue slices based on tissue percentage
    ## Also score the tiles by staining quality
    ## And save annotation image
    for i in range(len(tiles)):
        t_n = "0" + str(tiles[i].column) + "_0" + str(tiles[i].row)
        pil_img = tiles[i].image
        np_img = util.pil_to_np_rgb(pil_img)
        tp = filter.tissue_percent(np_img)

        # Handle by_tissue percentage selection
        if tp >= tp_threshold:
            # Add to selection
            l_tiles.append(tiles[i])

            # Score the staining quality
            score, color_factor, s_and_v_factor, quantity_factor = stain.score_tile(np_img, tp)
            tile_name.append(path[:-3] + "slice_0" + str(tiles[i].column) + "_0" + str(tiles[i].row) + ".jpg")
            s_score.append(score)
            s_color_factor.append(color_factor)
            s_s_and_v_factor.append(s_and_v_factor)
            s_quantity_factor.append(quantity_factor)

            # Create annotation tile
            pil_img_exp = ImageOps.expand(pil_img, border=2, fill="green")
            draw = ImageDraw.Draw(pil_img_exp)
            draw.text((0, 0), t_n, fill="green")
            s_tiles[i].image = pil_img_exp

        # Handle other tiles
        else:
            pil_img_exp = ImageOps.expand(pil_img, border=2, fill="white")
            draw = ImageDraw.Draw(pil_img_exp)
            draw.text((0, 0), t_n, fill="white")
            s_tiles[i].image = pil_img_exp

    # Join annotated tiles and save
    s_tiles = image_slicer.join(s_tiles)
    # Remove the alpha channel if any
    s_tiles = s_tiles.convert("RGB")
    s_tiles.save("slice_" + "annotation_image.jpg")

    # Construct annotation table
    stats_s_tiles = pd.DataFrame()
    stats_s_tiles["Name"] = tile_name
    stats_s_tiles["score"] = s_score
    stats_s_tiles["color_factor"] = s_color_factor
    stats_s_tiles["s_and_v_factor"] = s_s_and_v_factor
    stats_s_tiles["quantity_factor"] = s_quantity_factor

    ## Save Stain quality score for tiles, re: further rank the tiles
    stats_s_tiles.to_csv(os.path.join(n_path, "stain_scores.csv"), index=False)

    ## Save extracted tiles to file
    image_slicer.save_tiles(l_tiles, directory=n_path,
                            prefix="slice", format="JPEG")

def multi_get_tiles_score_save(path, sl_format, tp_threshold=80):
    """
    Apply a set of filters to image folder

    :param path: The image folder.
    :param sl_format: The file format of the images.
    :param tp_threshold: The percentage tissue quantity to retain.
    :return: Tuple of 1) Dictionary of mask percentage and and path to filtered images.
    """
    timer = Time()

    # List the files
    files = os.listdir(path)
    print("Tilling {} images".format(len(files)))


    for i in files:
        if i.endswith(sl_format):
            sl = str(os.path.join(path, i))
            get_tiles_score_save(sl, tp_threshold=tp_threshold)
            timer.elapsed_display()
    return path




