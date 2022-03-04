"""
Macenko et al., 2009, pp. 1107–1110.

"""

from __future__ import division
import numpy as np
import os
import iwspp.flows.util as ut


def get_stain_matrix(I, beta=0.15, alpha=1):
    """
    Get stain matrix (2x3)
    :param I:
    :param beta:
    :param alpha:
    :return:
    """
    OD = ut.RGB_to_OD(I).reshape((-1, 3))
    OD = (OD[(OD > beta).any(axis=1), :])
    _, V = np.linalg.eigh(np.cov(OD, rowvar=False))
    V = V[:, [2, 1]]
    if V[0, 0] < 0: V[:, 0] *= -1
    if V[0, 1] < 0: V[:, 1] *= -1
    That = np.dot(OD, V)
    phi = np.arctan2(That[:, 1], That[:, 0])
    minPhi = np.percentile(phi, alpha)
    maxPhi = np.percentile(phi, 100 - alpha)
    v1 = np.dot(V, np.array([np.cos(minPhi), np.sin(minPhi)]))
    v2 = np.dot(V, np.array([np.cos(maxPhi), np.sin(maxPhi)]))
    if v1[0] > v2[0]:
        HE = np.array([v1, v2])
    else:
        HE = np.array([v2, v1])
    return ut.normalize_rows(HE)

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
        return ut.OD_to_RGB(self.stain_matrix_target)

    def transform(self, I):
        I = ut.standardize_brightness(I)
        stain_matrix_source = get_stain_matrix(I)
        source_concentrations = ut.get_concentrations(I, stain_matrix_source)
        maxC_source = np.percentile(source_concentrations, 99, axis=0).reshape((1, 2))
        maxC_target = np.percentile(self.target_concentrations, 99, axis=0).reshape((1, 2))
        source_concentrations *= (maxC_target / maxC_source)
        return (255 * np.exp(-1 * np.dot(source_concentrations, self.stain_matrix_target).reshape(I.shape))).astype(
            np.uint8)

    def hematoxylin(self, I):
        I = ut.standardize_brightness(I)
        h, w, c = I.shape
        stain_matrix_source = get_stain_matrix(I)
        source_concentrations = ut.get_concentrations(I, stain_matrix_source)
        H = source_concentrations[:, 0].reshape(h, w)
        H = np.exp(-1 * H)
        return H

    def Eosin(self, I):
        I = ut.standardize_brightness(I)
        h, w, c = I.shape
        stain_matrix_source = get_stain_matrix(I)
        source_concentrations = ut.get_concentrations(I, stain_matrix_source)
        H = source_concentrations[:, 1].reshape(h, w)
        H = np.exp(-1 * H)
        return H

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
  # n_path1 = os.path.join(path, "haematoxylin")
  print(n_path)

  files = [f for f in os.listdir(path) if f.endswith(sl_format)]
  print("Applying filters to {} image".format(len(files)))

  if not os.path.exists(n_path):
    os.makedirs(n_path)
    # os.makedirs(n_path1)

  for i in files:
    sl = ut.read_image(os.path.join(path, i))
    sl1 = sd_class.transform(sl)
    # sl2 = sd_class.hematoxylin(sl)

    sl1 = ut.np_to_pil(sl1)
    # sl2 = ut.np_to_pil(sl2)

    sl1.save(os.path.join(n_path, i))
    # sl2.save(os.path.join(n_path1, i))

  timer.elapsed_display()
  return
