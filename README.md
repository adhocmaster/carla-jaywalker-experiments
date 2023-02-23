# Installation -


Step 1: create a conda environment named "carla37" with python version 3.7.9 and activate it
```
conda create -n carla37 python=3.7.9
conda activate carla37
```

Step 2: clone this repo to your machine and navigate to the root folder in terminal


## windows
Step 3: Update the environment with all the necessary packages needed for this repository
```
conda env update -n carla37 --file environment.yml
```
Now you can run the experiments

## Ubuntu
Step 3: Update the environment with all the necessary packages needed for this repository
```
conda env update -n carla37 --file environment-ubuntu-mac.yml
```
Now you can run the experiments. If you run into issues while installing packages from the previous command. Try installing with the following commands.

```
pip install carla
conda install numpy
conda install matplotlib

conda install -c anaconda click
conda install -c anaconda eventlet
conda install -c intel networkx
conda install -c conda-forge pandas
conda install -c cctbx202008 pyyaml
conda install -c cctbx202112 scipy
conda install -c conda-forge shapely
conda install -c anaconda seaborn
pip install pygame==1.9.6

conda install -c conda-forge gym
```



# Running experiments

There are three ways experiments can be run, based on scenarios, and based on the research settings. Research settings are more useful for pedestrian behavior modeling and the scenarios are useful for ego vehicle modeling. Leaderboard scenarios are for evaluation.

## Running Scenarios

    python scenario_runner2.py --scenario Scenario1v1_1 --configFile ./research/Scenario1v1.xml --reloadWorld
    python scenario_runner2.py --route ./srunner/data/routes_devtest.xml ./srunner/data/all_towns_traffic_scenarios.json 0  (open python manual_control.py in another terminal with the same env)
    python scenario_runner2.py --route ./srunner/data/routes_devtest.xml ./srunner/data/all_towns_traffic_scenarios.json 0 --agent ./leaderboard/autoagents/human_agent.py 
    python scenario_runner2.py --route ./srunner/data/routes_devtest.xml ./srunner/data/all_towns_traffic_scenarios.json 0 --output --json --outputDir ./logs
    python scenario_runner2.py --route ./research/scenario_routes_short.xml ./research/scenario_locations.json 0 --debug

## Running Leaderboard Scenarios
    python leaderboard_evaluator.py --routes ./srunner/data/routes_devtest.xml -a ./leaderboard/autoagents/human_agent.py --route-id=1 --scenarios ./leaderboard/routes/atown2_3scenarios.json
    python leaderboard_evaluator2.py --routes ./research/scenario_routes_short.xml -a ./leaderboard/autoagents/human_agent.py --route-id=0 --scenarios ./research/scenario_locations.json

## Streaming
You can use the streamer.py file to stream from the spectator in a remote server. Issue this command in the terminal:
```
python streamer.py
```
It will prompt for ip and port.

## Running carla examples
Navigate to the carla examples folder from your carla installation folder. Run any experiment. The streamer should be able to show the simulation.
