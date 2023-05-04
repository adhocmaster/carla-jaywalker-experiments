# This is the settings file for the program
# Set the directory addresses accordingly

# Directory of the project (path for the highD_code folder)
# C:\Users\abjawad\Documents\GitHub\cogmod-human-driver-model\highd_tools\highd_tools
PROJECT_DIR = 'C:\\Users\\abjawad\\Documents\\GitHub\\cogmod-human-driver-model\\highd_tools'
# PROJECT_DIR = 'C:/Users/abjawad/Documents/GitHub/drone-dataset-tools/src/highD_code'

# Path for the HighD dataset  
DATA_DIRECTORY = 'C:\\Users\\abjawad\\Documents\\GitHub\\drone-dataset-tools\\data\\highD_dataset'
# DATA_DIRECTORY = "C:/Users/abjawad/Documents/GitHub/drone-dataset-tools/data/highD_dataset"

# Path for the output directory
OUTPUT_DIRECTORY = "C:\\Users\\abjawad\\Documents\\GitHub\\cogmod-human-driver-model\\highd_tools\\output"

# dillDir = "C:/Users/abjaw/Documents/GitHub/drone-dataset-tools/output/dill"
# outputDir = "C:/Users/abjaw/Documents/GitHub/drone-dataset-tools/output"


import os, sys

currentFolder = os.path.abspath('')
try:
    sys.path.remove(str(currentFolder))
except ValueError: # Already removed
    pass


projectFolder = PROJECT_DIR

sys.path.append(str(projectFolder))
os.chdir(projectFolder)
print( f"current working dir{os.getcwd()}")
