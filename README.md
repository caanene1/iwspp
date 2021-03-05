# iwspp
Preprocessing workflow for pathology slides

Pathology images are heterogeneous with widely varying staining intensities, tissue content 
and background artefacts. Current CNN require high-quality examples to achieve good results. 
iwspp implements several preprocessing workflows that can be generalised to these slides


# Installation and running the tool
The best way to get iwspp along with all the dependencies is to install the release with python package installer (pip)

```pip install iwspp```
or 
```pip install /iwspp/dist/iwspp-1.0.0-py3-none-any.whl```
This will add iwspp command line argument with -t for switching.

High number >2 -t options require the lower level analysis to work if starting scratch.

| Options | Context | Usage |
| ---    | --- | --- |
| t = 1 | SVS to small size images (.jpeg .png) | ```iwspp -t 1``` |
| t = 2 | Tissue segmentation | ```iwspp -t 2``` | 
| t = 3 | Tissue tilling | ```iwspp -t 3``` |
| t = 4 | Stain normalisation | ```iwspp -t 4``` |

Utility functions can be imported using conventional python system like ```from iwspp.Normalize import Macenko```