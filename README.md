# Front3D to USD batch processer based on BlenderProc2

_____
### Disclaimer:

Please check the official [repo](https://github.com/DLR-RM/BlenderProc/) if you have any problem with this code. I only modified some files.

Follow the installation instructions you can find [here](https://github.com/DLR-RM/BlenderProc/tree/a1af9a). I diverged at commit [a1af9a](https://github.com/eliabntt/Front3D_to_USD/commit/a1af9a80cc9fb02116445dd04f95ba073cdf1ed2). We did NOT test any updated version.
______

This repository was used within the [GRADE](https://eliabntt.github.io/GRADE-RR/) project to generate the FRONT 3D environments.
We used Windows with the Omniverse suggested drivers and CUDA version.

For the generation of the paper data we used blender connector (which you need to install see [here](https://docs.omniverse.nvidia.com/con_connect/con_connect/blender.html)) `3.1.0-usd.100.1.10`. Newer version should work out of the box.

Then you need to accept the licensing terms and download the FRONT3D and the FUTURE3D datasets [here](https://tianchi.aliyun.com/specials/promotion/alibaba-3d-scene-dataset)

Get also the `cc_textures` using [this](https://github.com/DLR-RM/BlenderProc/blob/main/blenderproc/scripts/download_cc_textures.py)
______

### How to run --- as per the paper

From the current folder in which you cloned the repository

`python cli.py debug examples\datasets\front_3d_with_improved_mat\my_main.py --front .\3D-FRONT\ --future_folder .\3D-FUTURE-model --front_3D_texture_path .\3D-FRONT-texture --cc_material_path .\cc_textures --temp_dir temp_dir --output_dir output --last_sample id --only_one True/False --custom-blender-path=C:\Users\ebonetto\AppData\Local\ov\pkg\blender-3.1.0-usd.100.1.10\Release`

You need to update all the folders. Preferably with absolute paths.

`--last_sample` is optional. You may specify an ID which is the last environment processed.
If you want to process only one environment put the corresponding argument as True.

The script will get the `json` files from the `--front` folder and process all of them. First it will load the `cc_materials` and then whitelist them to be able to clean the environment safely.

Then it will load the front3d world, exchange some of the materials randomly, and then export the environment.

The [exporter](https://github.com/eliabntt/Front3D_to_USD/blob/c0e2e44cf88578dabefa043f6e390cc5fe4361fb/blenderproc/python/writer/WriterUtility.py#L23) takes care of exporting the usd file, the x3d (which can be later converted to octomap), the blend file, the STL of the environment and a series of informations including the convex enclosing polygon, and [max,min][x,y,z] informations based on the walls.  

We made sure that each object is labelled according to the corresponding data from Front3D, however, note that this might be wrong [see here](https://github.com/DLR-RM/BlenderProc/issues/466).

The generated environments will be available upon acceptance of the paper. However, note that everything is open source so you can directly use them.

### How to run --- custom fbx environment converter

If you have an environment and you want to use the exporter simply load it in blender and call the [exporter](https://github.com/eliabntt/Front3D_to_USD/blob/c0e2e44cf88578dabefa043f6e390cc5fe4361fb/blenderproc/python/writer/WriterUtility.py#L23).

An example on how to do that can be found [here](https://github.com/eliabntt/Front3D_to_USD/blob/main/examples/datasets/front_3d_with_improved_mat/my_env_exporter.py).

Important arguments are the `join_all` which will be used to create a monolithic mesh during the export, which may cause crashing of the program for large environments, and `limit_names` used to compute the boundaries of the environment.

### How to get the environment for GRADE

Either use the fbx converter or export manually your own environment.
The STL file is not mandatory (you can disable it even within our code). Remember that without it our placement strategy cannot work.

The `npy` file with the limits of the environment (mainly used during placement and to limit the movement of the robot) can be easily manually created following [this](https://github.com/eliabntt/Front3D_to_USD/blob/c0e2e44cf88578dabefa043f6e390cc5fe4361fb/blenderproc/python/writer/WriterUtility.py#L117).

### Convert x3d to octomap

Get `binvox` from [here](https://www.patrickmin.com/binvox/)
Install `sudo apt-get install -y xsltproc octovis`

Run 
```
xsltproc --xincludestyle X3dToVrml97.xslt Desktop/vox.x3d --output myvox.wrl
./binvox -e myvox.wrl && binvox2bt myvox.binvox
```

See [here](https://www.patrickmin.com/binvox/) for additional options.

You can visualize the octomap with `octovis myvox.binvox.bt`

_____

The list of influential changes is:
- created `examples/datasets/front_3d_with_improved_mat/my_main.py` and `examples/datasets/front_3d/my_main.py`
- created `examples/datasets/front_3d_with_improved_mat/my_env_exporter.py`
- edited `examples/datasets/front_3d/config.yaml` to use the Omniverse blender installation
- edited `blenderproc/python/writer/WriterUtility.py`  adding `export_environment` function and related libraries
- edited `blenderproc/python/utility/InstallUtility.py` to use the correct path based on the omniverse installation
- edited `blenderproc/python/utility/Initializer.py` to pass a whitelist to the `cleanup` and `_remove_all_data` methods, and a `_get_all_data()` method. This is used to clean the environment after every generation.
- edited `blenderproc/__init__.py` to load `get_whitelist`
- edited `blenderproc/python/loader/Front3DLoader.py` to get random light coloring and intensity, delete the camera and add an additional mapping procedure to save more infos about the possibly wrong category

There are other minor edits regarding AMASS (to be able to load a sequence) but those are not relevant to the project.

All changes can be found [here](https://github.com/DLR-RM/BlenderProc/compare/main...eliabntt:Front3D_to_USD:c0e2e44#).

## Citation

If you find this work useful please consider citing...

## License
By using this software or any of its derivation, including the data, you are implicitly accepting all the corresponding licenses, including but not limited to, the ones from BlenderProc, GRADE-RR, GRADE, 3D Front, 3D Future, ambientcg, MPI-PS.
