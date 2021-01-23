# ACSNI
Pathology slide processor for DIpat.
This tool is built in python3 with openslide backend.

# To clone the source repository 
git clone https://github.com/caanene1/iwsprepro

# Installing the requirements 
The best way to get all the dependencies for this tool is to install the "requirements.txt" included in the root directory.

On  Linux and Mac OS::
pip install -r requirements.txt

On Windows OS::
python -m pip install -U pip setuptools

# Input



# Running the tool
To see input parameters use:

python main.py -help

```main.py [-h] [-m MAD] [-b BOOT] [-p LP] [-f FULL]```

```optional arguments:
  -h,       --help        show this help message and exit
  -m MAD,   --mad MAD     Minimum median absolute deviance for geneSets
  -b BOOT,  --boot BOOT   Number of ensemble models to run
  -p LP,    --lp LP       Percentage of gene set for model layers


```

```python ACSNI.py -i expression.csv -t GeneSets.csv```

# Examples 
Example files are included in the "example data" folder.
