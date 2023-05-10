import os, sys

# This is the settings file for the program
# Set the directory addresses accordingly

# Directory of the project (path for the highD_tools folder)

PROJECT_DIR = r'C:\\Users\\abjaw\\Documents\\GitHub\\CogMod-driver-behavior-model\\highd_tools'

# Path for the HighD dataset  
DATA_DIRECTORY = r'C:\\Users\\abjaw\\Documents\\GitHub\\highD-dataset\\Python\\data'

# Path for the output directory
OUTPUT_DIRECTORY = r"C:\\Users\\abjaw\\Documents\\GitHub\\CogMod-driver-behavior-model\\highd_tools\\output"

# Path for the dill directory
DILLDIR = r"C:\\Users\\abjaw\\Documents\\GitHub\\CogMod-driver-behavior-model\\highd_tools\\dill"



currentFolder = os.path.abspath('')
try:
    sys.path.remove(str(currentFolder))
except ValueError: # Already removed
    pass


projectFolder = PROJECT_DIR

sys.path.append(str(projectFolder))
os.chdir(projectFolder)
print( f"current working dir{os.getcwd()}")
