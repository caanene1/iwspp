import shutil, os
import pandas as pd


def move_single_folder(o_path, n_path, target="selectedTiles", f_format=".jpg",
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
        sub_folder = os.path.join(o_path, i, target)
        an_note.append(pd.read_csv(os.path.join(sub_folder, annotation)))

        files = [t for t in os.listdir(sub_folder) if t.endswith(f_format)]
        files = [t for t in files if not t.startswith(annotation[:-4])]

        for z in files:
            shutil.move(os.path.join(sub_folder, z),
                        os.path.join(n_path, i + "_" + z))

    an_note = pd.concat(an_note, axis=0)
    an_note = an_note.reset_index()

    an_note.to_csv(os.path.join(n_path, annotation), index=False)
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


