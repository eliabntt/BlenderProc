import blenderproc as bproc
import argparse
import os,glob
import numpy as np
import bpy, bmesh
import sys
import ipdb
import math
import random
from blenderproc.python.writer.WriterUtility import export_environment

parser = argparse.ArgumentParser()
parser.add_argument("--front", help="Path to the 3D front folder with jsons")
parser.add_argument("--future_folder", help="Path to the 3D Future Model folder.")
parser.add_argument("--front_3D_texture_path", help="Path to the 3D FRONT texture folder.")
parser.add_argument('--cc_material_path', nargs='?', default="resources/cctextures", help="Path to CCTextures folder, see the /scripts for the download script.")
parser.add_argument("--output_dir", help="Path to where the data should be saved")
parser.add_argument("--temp_dir", help="Path to local disk temporary directory. Necessary since some writers cannot write directly to network locations")
parser.add_argument("--last_sample", help="Last sample processed (will reprocess)", default="")
parser.add_argument("--only_one", help="Process only one (last_sample/first)", default=False)
args = parser.parse_args()

front_output_dir = args.output_dir

cnt = 0
path = os.path.abspath(args.front)
listed = glob.glob(os.path.join(path,'*.json'))
listed.sort()
found = (args.last_sample == "")
whitelist = []
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping.csv"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)
cc_materials = []

for i in listed:
    if not found:
        if args.last_sample in i:
            found = True
        else:
            continue
    try_count = 0
    succeed = False
    while try_count <= 5 and not succeed:
        myworld = os.path.join(path, i)
        print(myworld)

        out_dir = os.path.join(front_output_dir, os.path.basename(myworld)[:-5])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        if not os.path.exists(myworld) or not os.path.exists(args.future_folder):
            raise Exception("One of the two folders does not exist!")

        if cnt % 10 == 0:
            bproc.init()
            cc_materials = bproc.loader.load_ccmaterials(args.cc_material_path,
                                                         ["Bricks", "Wood", "Carpet", "Tile", "Marble"])
            whitelist = bproc.get_whitelist()
            cnt = 1
        else:
            bproc.init(whitelist=whitelist)
            cnt += 1

        with open(os.path.join(out_dir, f"out_{try_count}.txt"), "w") as file_out, open(
                os.path.join(out_dir, f"err_{try_count}.txt"), "w") as file_err:
            try_count += 1
            try:
                sys.stdout = file_out
                sys.stderr = file_err

                # load the front 3D objects
                loaded_objects = bproc.loader.load_front3d(
                    json_path=myworld,
                    future_model_path=args.future_folder,
                    front_3D_texture_path=args.front_3D_texture_path,
                    label_mapping=mapping,
                    random_light_color=False,
                    ceiling_light_strength=0,
                    lamp_light_strength=0,
                    random_light_intensity=True
                )

                floors = bproc.filter.by_attr(loaded_objects, "name", "Floor.*", regex=True)
                for floor in floors:
                    # For each material of the object
                    for i in range(len(floor.get_materials())):
                        # In 95% of all cases
                        if np.random.uniform(0, 1) <= 0.95:
                            # Replace the material with a random one
                            floor.set_material(i, random.choice(cc_materials))

                baseboards_and_doors = bproc.filter.by_attr(loaded_objects, "name", "Baseboard.*|Door.*", regex=True)
                wood_floor_materials = bproc.filter.by_cp(cc_materials, "asset_name", "WoodFloor.*", regex=True)
                for obj in baseboards_and_doors:
                    # For each material of the object
                    for i in range(len(obj.get_materials())):
                        # Replace the material with a random one
                        obj.set_material(i, random.choice(wood_floor_materials))

                walls = bproc.filter.by_attr(loaded_objects, "name", "Wall.*", regex=True)
                marble_materials = bproc.filter.by_cp(cc_materials, "asset_name", "Marble.*", regex=True)
                for wall in walls:
                    # For each material of the object
                    for i in range(len(wall.get_materials())):
                        # In 50% of all cases
                        if np.random.uniform(0, 1) <= 0.4:
                            # Replace the material with a random one
                            wall.set_material(i, random.choice(marble_materials))

                filepath=os.path.join(out_dir,os.path.basename(myworld)[:-4]+"usd")
                temp_filepath = os.path.join(args.temp_dir,os.path.basename(myworld)[:-4]+"usd")

                export_environment(temp_filepath, filepath)

                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete()
                succeed = True
            except:
                import traceback
                sys.stderr.write('error\n')
                sys.stderr.write(traceback.format_exc())
            finally:
                sys.stdout.flush()
                sys.stderr.flush()
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

    if args.only_one != False:
        break