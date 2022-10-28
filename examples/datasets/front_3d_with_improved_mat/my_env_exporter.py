import blenderproc as bproc
import argparse
import os,glob
import numpy as np
import bpy, bmesh
import sys
import ipdb
from blenderproc.python.writer.WriterUtility import export_environment

parser = argparse.ArgumentParser()
parser.add_argument("--env", help="Path to the env file")
parser.add_argument("--output_dir", help="Path to where the data should be saved")
parser.add_argument("--temp_dir", help="Path to where the data should be temporary saved")
parser.add_argument("--export_usd", default="False", help="Wether to export the usd or not")
parser.add_argument("--join_all", default="False", help="Wether to join all assets. Default to false to avoid crashes")
parser.add_argument("--limit_names", default="",nargs='?', help="Obj names to be used for computing limits separated by space, if empty use \"floor\" and \"wall\"")
args = parser.parse_args()

env_out_dir = args.output_dir
if not os.path.exists(env_out_dir):
    os.makedirs(env_out_dir)
env = args.env
bproc.init()
for o in bpy.context.scene.objects:
    o.select_set(True)
    
# Call the operator only once
bpy.ops.object.delete()

with open(os.path.join(env_out_dir, f"out.txt"), "w") as file_out, open(
    os.path.join(env_out_dir, f"err.txt"), "w") as file_err:
    try:
        sys.stdout = file_out
        sys.stderr = file_err
        bpy.ops.import_scene.fbx(filepath=env)

        filepath=os.path.join(env_out_dir,os.path.basename(env)+".usd")
        temp_filepath = os.path.join(args.temp_dir,os.path.basename(env)+".usd")

        if args.limit_names == "":
            export_environment(temp_filepath, filepath, args.export_usd != "False", join_all=(args.join_all != "False"))
        else:
            export_environment(temp_filepath, filepath, args.export_usd != "False", str.split(args.limit_names), args.join_all != "False")
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