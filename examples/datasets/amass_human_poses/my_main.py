import blenderproc as bproc
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('amass_dir', nargs='?', default="resources/AMASS", help="Path to the AMASS Dataset folder")
parser.add_argument('output_dir', nargs='?', default="examples/datasets/amass_human_poses/output", help="Path to where the final files will be saved")
args = parser.parse_args()

bproc.init()

# Load the objects into the scene
objs = bproc.loader.load_AMASS_seq(
    args.amass_dir,
    sub_dataset_id="CMU",
    body_model_gender="male",
    subject_id="10",
    sequence_id=1
)