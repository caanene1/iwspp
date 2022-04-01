"""
Macenko et al., 2009, pp. 1107–1110.

"""

from __future__ import division
import numpy as np
import os
import iwspp.flows.util as ut


def get_stain_matrix(x, beta=0.15, alpha=1):
    """
    Get stain matrix (2x3)

    Args:
        x: Image to process
        beta: first threshold
        alpha: Second threshold
    """

    od = ut.convert_rgb_od(x, t="od").reshape((-1, 3))
    od = (od[(od > beta).any(axis=1), :])
    _, vv = np.linalg.eigh(np.cov(od, rowvar=False))
    vv = vv[:, [2, 1]]
    if vv[0, 0] < 0: vv[:, 0] *= -1
    if vv[0, 1] < 0: vv[:, 1] *= -1
    that = np.dot(od, vv)
    phi = np.arctan2(that[:, 1], that[:, 0])
    min_phi = np.percentile(phi, alpha)
    max_phi = np.percentile(phi, 100 - alpha)
    v1 = np.dot(vv, np.array([np.cos(min_phi), np.sin(min_phi)]))
    v2 = np.dot(vv, np.array([np.cos(max_phi), np.sin(max_phi)]))
    if v1[0] > v2[0]:
        he = np.array([v1, v2])
    else:
        he = np.array([v2, v1])
    return ut.normalize_rows(he)

class Normalizer(object):
    """
    A stain normalization object
    """

    def __init__(self):
        self.stain_matrix_target = None
        self.target_concentrations = None

    def fit(self, target):
        target = ut.standardize_brightness(target)
        self.stain_matrix_target = get_stain_matrix(target)
        self.target_concentrations = ut.get_concentrations(target, self.stain_matrix_target)

    def target_stains(self):
        return ut.convert_rgb_od(self.stain_matrix_target, t="rgb")

    def transform(self, x):
        x = ut.standardize_brightness(x)
        stain_matrix_source = get_stain_matrix(x)
        source_concentrations = ut.get_concentrations(x, stain_matrix_source)
        max_c_source = np.percentile(source_concentrations, 99, axis=0).reshape((1, 2))
        max_c_target = np.percentile(self.target_concentrations, 99, axis=0).reshape((1, 2))
        source_concentrations *= (max_c_target / max_c_source)
        return (255 * np.exp(-1 * np.dot(source_concentrations, self.stain_matrix_target).reshape(x.shape))).astype(
            np.uint8)

    def hematoxylin(self, x):
        x = ut.standardize_brightness(x)
        h, w, c = x.shape
        stain_matrix_source = get_stain_matrix(x)
        source_concentrations = ut.get_concentrations(x, stain_matrix_source)
        hh = source_concentrations[:, 0].reshape(h, w)
        hh = np.exp(-1 * hh)
        return hh

    def Eosin(self, x):
        x = ut.standardize_brightness(x)
        h, w, c = x.shape
        stain_matrix_source = get_stain_matrix(x)
        source_concentrations = ut.get_concentrations(x, stain_matrix_source)
        hh = source_concentrations[:, 1].reshape(h, w)
        hh = np.exp(-1 * hh)
        return hh

def multi_apply_normalisation_to_images(path, nn_path, sl_format):
  """
  Apply normalisation to a set of slides
  Args:
    path: The image folder.
    nn_path: The path to standard.
    sl_format: The format of the image to normalise.

  Returns:
    Saves to normalisation folder
  """

  timer = ut.Time()
  sd = ut.read_image(nn_path)
  sd_class = Normalizer()
  sd_class.fit(sd)

  n_path = os.path.join(path, "normalised")
  print(n_path)

  files = [f for f in os.listdir(path) if f.endswith(sl_format)]
  print("Applying filters to {} image".format(len(files)))

  if not os.path.exists(n_path):
    os.makedirs(n_path)

  for i in files:
    sl = ut.read_image(os.path.join(path, i))
    sl1 = sd_class.transform(sl)
    sl1 = ut.np_to_pil(sl1)
    sl1.save(os.path.join(n_path, i))

  timer.elapsed_display()
  return
