# Creating a new map in Roadrunner and importing into Carla

## Prerequisites
1. x64 Visual Studio Terminal.
2. OS level default python installation with carla package (pip install carla) 0.9.13

## Steps
1. export map from road runner (fbx + opendrive)
2. Importing the fbx map into **Carla Editor**

    i. copy the files to Import folder in carla source (**src/carla/Import**). All the maps will be built into a single package from this folder. You may want to remove old maps if you want.

    ii. Open x64 VS terminal and navigate to **src/carla** folder. Run the following command. This will compile the map and also import it to the Carla Editor. *If there is no system python installation with carla package, it will produce an error.*
    ```
    make import  ARGS="--package=<package_name>"
    ```

    iii. open map in Carla editor using the following command in **src/carla** folder. Maps are levels. You should be able to see a folder with your package name when you open a level.
    ```
    make launch-only
    ```
3. Creating the map obj file:

    i. Add some crosswalks with naming convention such as xxx_Road_Crosswalk_xxx (wrong convention will not create nav for peds). *This step is only necessary for automated pedestrian navigation*

    ii. Add "NoExport" tag to BP_Sky object. Otherwise, the nav build will fail.

    iii. Select all components are do File -> Carla Export. This will create object files that can be converted to binary files which can be used by the simulator (which is a game). The file is saved in **src/carla/Unreal/CarlaUE4/Saved/** folder.

4. (Optional) Creating walker navigation and converting the obj file to binary:
    i. move src/carla/Unreal/CarlaUE4/Saved/<map_name>.obj -> src/carla/Util/DockerUtils/dist

    ii. run Util/DockerUtils/dist/build.bat <map_name> (without ext) to build walker navigation paths.

    iii. copy <map_name>.bin to src/carla/Unreal/CarlaUE4/Content/your-map-package/Maps/map_name/Nav folder (This is the actual map folder of a single map where you have TM and OpenDrive folders. Putting in the package where multiple maps reside is not working.)

5. make re-distributable package of maps from the binary file.

    1. In your carla source folder, run **make package ARGS="--packages=package_name"**. This command takes your edited map from the Unreal/CarlaUE4/Content folder. So, create navigation before packaging. This will produce the importable packages in src/carla/Build/UE4Carla. 

    2. Unpack the zipped folder if not already existing. Copy your package from **CarlaUE4/Content/you-package-name** to your carla Content folder (not the engine content folder)

    3. You will see a json file in CarlaUE4/Content/Carla/Config with your package name. Copy that to the same folder of your Carla distribution. Without this file, map may not load. Nothing else is needed from Carla content folder.

    4. Ignore rest of the files/folders. (delete the Engine folder)
    make

