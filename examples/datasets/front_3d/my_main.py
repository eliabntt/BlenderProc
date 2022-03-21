import blenderproc as bproc
from scipy.spatial import ConvexHull
import argparse
import os,glob
import numpy as np
import bpy, bmesh
import shutil
import sys
import ipdb
import math
import random

parser = argparse.ArgumentParser()
parser.add_argument("front", help="Path to the 3D front file")
parser.add_argument("future_folder", help="Path to the 3D Future Model folder.")
parser.add_argument("front_3D_texture_path", help="Path to the 3D FRONT texture folder.")
parser.add_argument("output_dir", help="Path to where the data should be saved")
args = parser.parse_args()

front_output_dir = "P:\\irotate\\3DFRONT\\USD-exports"

cnt = 0
path = os.path.abspath(os.path.join(args.front, os.pardir))
listed = glob.glob(os.path.join(path,'*.json'))
listed.sort()
found = True
tobefound = "008699e0-8d00-40f3-92b4-72347fa892c1"
for i in listed:
    if tobefound in i:
        found= True
    if not found:
        continue
    try:
        myworld = os.path.join(path,i)
        print(myworld)

        out_dir = os.path.join(front_output_dir, os.path.basename(myworld)[:-5])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        file_out = open(os.path.join(out_dir, "out.txt"), "w")
        file_err = open(os.path.join(out_dir, "err.txt"), "w")

        sys.stdout = file_out
        sys.stderr = file_err

        if not os.path.exists(myworld) or not os.path.exists(args.future_folder):
            raise Exception("One of the two folders does not exist!")

        bproc.init()
        mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping.csv"))
        mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

        # set the light bounces
        bproc.renderer.set_light_bounces(diffuse_bounces=200, glossy_bounces=200, max_bounces=200,
                                          transmission_bounces=200, transparent_max_bounces=200)

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

        filepath=os.path.join(out_dir,os.path.basename(myworld)[:-4]+"usd")
        
        temp_filepath = os.path.join(args.output_dir,os.path.basename(myworld)[:-4]+"usd")
        
        bpy.ops.wm.usd_export(filepath=temp_filepath,
        filemode=8,display_type='DEFAULT',sort_method='DEFAULT',
        selected_objects_only=False,visible_objects_only=False,export_animation=False,
        export_hair=True,export_vertices=True,export_vertex_colors=True,
        export_vertex_groups=False,export_face_maps=True,export_uvmaps=True,export_normals=True,
        export_transforms=True,export_materials=True,export_meshes=True,export_lights=True,export_cameras=False,
        export_curves=True,export_particles=True,export_armatures=False,use_instancing=False,
        evaluation_mode='RENDER',default_prim_path="/world",root_prim_path="/world",material_prim_path="/world/materials",
        generate_cycles_shaders=True,generate_preview_surface=True,generate_mdl=True,convert_uv_to_st=True,convert_orientation=True,
        convert_to_cm=True,export_global_forward_selection='Y',export_global_up_selection='Z',export_child_particles=True,
        export_as_overs=False,merge_transform_and_shape=False,export_custom_properties=True,export_identity_transforms=False,
        apply_subdiv=True,author_blender_name=True,vertex_data_as_face_varying=False,frame_step=1,override_shutter=False,
        init_scene_frame_range=False,export_textures=False,relative_texture_paths=False,light_intensity_scale=1,
        convert_light_to_nits=True,scale_light_radius=True,convert_world_material=True)
        
        shutil.move(temp_filepath, filepath)
        filepath=filepath[:-3]+"x3d"
        bpy.ops.export_scene.x3d(filepath=filepath, use_selection=False, use_mesh_modifiers=True, use_normals=True, use_hierarchy=True,
         name_decorations=True, global_scale=1.0, path_mode='AUTO', axis_forward='Y', axis_up='Z')
        
        bpy.ops.wm.save_as_mainfile(filepath=filepath[:-3]+"blend")
        
        fz = -10
        for obj in bpy.data.objects:
            if "floor" in obj.name.lower():
                for v in obj.data.vertices:
                   h = (obj.matrix_world @ v.co)[2]
                   if h > fz: fz = h
                break

        bpy.ops.object.select_by_type(type='MESH')
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                break
        bpy.ops.object.join()

        mx = 999999
        my = 999999
        mz = 999999
        MX = -999999
        MY = -999999
        MZ = -999999
        pts = []
        for obj in bpy.data.objects:
            if obj.type != 'LIGHT':
                for v in obj.data.vertices:
                    l = obj.matrix_world @ v.co
                    pts.append([l[0],l[1]])
                    if l[0] < mx: mx = l[0]
                    if l[0] > MX: MX = l[0]
                    if l[1] < my: my = l[1]
                    if l[1] > MY: MY = l[1]
                    if l[2] < mz: mz = l[2]
                    if l[2] > MZ: MZ = l[2]
                break

        hull = ConvexHull(pts)
        my_hull = []
        for i in hull.vertices:
            my_hull.append([pts[i][0],pts[i][1]])

        my_hull = np.array(my_hull)
        my_hull_rolled = np.roll(my_hull, (1,1))
        my_hull_diff = my_hull - my_hull_rolled
        angle_diffs = np.arctan2(my_hull_diff[:,1],my_hull_diff[:,0])
        added = 0
        import copy
        backup = copy.deepcopy(my_hull)
        for index, angle in enumerate(angle_diffs % (np.pi/2)):
            if angle>0.1:
                pt0 = backup[index-1]
                pt1 = backup[index]
                if (math.remainder(angle_diffs[index], np.pi) < 0):
                    new_pt = np.array([pt1[0],pt0[1]])
                else:
                    new_pt = np.array([pt0[0],pt1[1]])
                print(new_pt)
                my_hull = np.insert(my_hull, index+added, new_pt, axis=0)
                added += 1

        np.save(filepath[:-3]+"npy", [mx, my, max(fz,mz), MX, MY, MZ, my_hull])
        print(filepath)

        bpy.ops.export_mesh.stl(filepath=filepath[:-3]+"stl", use_selection=True, global_scale=1, ascii=False, use_mesh_modifiers=True, batch_mode='OFF', axis_forward='Y', axis_up='Z')
        sys.stderr.flush()
        sys.stdout.flush()
        file_out.close()
        file_err.close()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    except:
        
        import traceback
        
        sys.stderr.write('error\n')
        sys.stderr.write(traceback.format_exc())

        
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        print('error')
        print(traceback.format_exc())
        
        sys.stdout.flush()
        sys.stderr.flush()
        file_err.close()
        file_out.close()