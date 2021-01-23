#!/usr/bin/env python

from SRC import slide, filter, tiles

parser = argparse.ArgumentParser(description="Preprocess pathology slides for image anslysis.")

parser.add_argument('-p', '--path', required=True, type=str,
                    help="Full path to the folder containing your slide files")
parser.add_argument('-f', '--format', default="svs", required=False, type=str,
                    help="The type of slide files, shoudl all be the same, defualts to .svs")
parser.add_argument('-s', '--save', default=".jpg", required=False,type=str,
                    help="The format to save the processed image, defaults to .jgp")
                    
parser.add_argument('-c', '--alpha', default=70, required=False, type=float,
                    help="Tissue perentage threshold for selecting tiles, defualts to 70")
                

args = parser.parse_args()
########################################################################################################

## Set arguments
path_sl = args.path
in_format = args.format
out_format = args.save
threshold_t = args.alpha
########################################################################################################

## Convert to smaller images
path_img = slide.multi_slides_to_images(path_sl, in_format)

## Mask non-tissue area
mask_percent, path_filter = filter.multi_apply_filters_to_images(path_img, out_format)

## Get Tiles
tiles.multi_get_tiles_score_save(path_filter, out_format, tp_threshold=threshold_t)








