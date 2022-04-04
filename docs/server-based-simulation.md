# selecting gpu
Run engine with -r.GraphicsAdapter=[0-9] command-line argument or add it under RendererSettings of Config/DefaultEngine.ini

# window size & fps

    .\CarlaUE4.exe -fps=15 -windowed -ResX=800 -ResY=600 -r.GraphicsAdapter=0

# startup map

    .\CarlaUE4.exe /Game/ADL_Maps_Carla_Materials/Maps/circle_t_junctions/circle_t_junctions

Inside engine /Game is an alias for the content folder.

# rpc and streaming port & off-screen rendering

.\CarlaUE4.exe -RenderOffScreen -carla-rpc-port=2000

