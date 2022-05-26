import shutil
import os
import pandas as pd


def move_single_folder(o_path, n_path, target="non", f_format=".jpg",
                       annotation="annotation.csv"):
    """
    Merge sub folders into a single folder.
    Ideal for cnn training.
    Args:
      o_path: Old path with sub folders.
      n_path: New save path.
      target: Name of sub folders to merge.
      f_format: File extension to target.
      annotation: Name of annotation file.
    Returns:
      Save files to new folder.
    """

    an_note = list()

    if not os.path.exists(n_path):
        os.makedirs(n_path)

    folders = [f for f in os.listdir(o_path) if not f.startswith(".DS_Store")]


    for i in folders:

        if target == "non":
            sub_folder = os.path.join(o_path, i)

        else:
           sub_folder = os.path.join(o_path, i, target)

        an_note.append(pd.read_csv(os.path.join(sub_folder, annotation)))

        files = [t for t in os.listdir(sub_folder) if t.endswith(f_format)]
        files = [t for t in files if not t.startswith(annotation[:-4])]

        for z in files:
            try:
                shutil.move(os.path.join(sub_folder, z), os.path.join(n_path, z))

            except FileNotFoundError:
                print("{} file has issue and was not save".format(sub_folder + z))

    an_note = pd.concat(an_note, axis=0)
    an_note = an_note.reset_index()

    try:
        an_note.to_csv(os.path.join(n_path, annotation), index=False)
    except FileNotFoundError:
        print("{} file has issue and was not saved".format(n_path + annotation))

    return


def add_annotation_file(source, meta="meta.csv", pattern=".jpg"):
    """
    Add annotation file to the folders.

    Args:
        source: The path to the source folder
        meta: The name of the file to add
        pattern: The file extension to target for the meta file

    """

    base_file = pd.DataFrame(columns=['Use', 'Tumour', 'nuclei_prop','immune_cells','white_prop', 'comment'])
    folders = [f for f in os.listdir(source)]

    for i in folders:
        files = [f for f in os.listdir(os.path.join(source, i)) if f.endswith(pattern)]
        out_file = pd.DataFrame()
        out_file["Name"] = files
        out_file = pd.concat([out_file, base_file], axis=1)
        out_file.to_csv(os.path.join(source, i, meta), index=False)

    return


def move_by_pattern(source, destination, pattern="-DX"):
    """
    Move folders with specific pattern to a new destination.

    Args:
        source: The path to the source folder
        destination: The path tp the destination folder (auto created if needed)
        pattern: The matching pattern

    """

    if not os.path.exists(destination):
        os.makedirs(destination)

    folders = [f for f in os.listdir(source) if pattern in f]

    for i in folders:
        shutil.move(os.path.join(source, i), os.path.join(destination, i))

    return


def clean_folder(path, target):
    # Decide later if this is worth keeping, probably not needed
    inputf = pd.read_csv("/Users/chineduanene/Documents/WorkSpace/CNN_pathology/Data/CNN_notNorm/lables.csv")
    keep = inputf["Name"].values
    path = "/Users/chineduanene/Documents/WorkSpace/CNN_pathology/Data/CNN_notNorm/images"
    files = os.listdir(path)


    for i in files:
        if i in keep:
            print("Yes")
        else:
            print("No")
            os.remove(os.path.join(path, i))

    return


## Usage
# add_annotation_file(source = "/Volumes/HDD1/Research/SCC/hypoxia/USET")
# op = "/Volumes/HDD1/Research/SCC/hypoxia/USET"
# np = "/Volumes/HDD1/Research/SCC/hypoxia/merged"
# move_single_folder(o_path=op, n_path=np, target="non", annotation="meta.csv")

