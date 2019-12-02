""" 
Original Authors: Py and Papr 
Adapted and commented by Tom Bullock, UCSB Attention Lab
Date: Nov 26th 2019 (latest update)

Purpose: 
Loop through recordings in a specified directory
Update to latest version of recording format (if recorded in legacy format)
Export annotation data, pupil diameter data and gaze position on surface data to .csv files 

Notes: 
Runs in python 3
Needs numpy, scipy, pandas
Needs av: conda install -c conda-forge av
Needs cv: conda install-c conda-forge opencv
Needs msgpack 0.5.6 (latest version [6] breaks the export): conda install -c anaconda msgpack-python=0.5.6  # possibly anaconda3? 
Needs modules from pupil/pupil_src/shared modules (git clone https://github.com/pupil-labs/pupil)

IMPORTANT: I had to comment out line 26 in "update_methods.py" (from video_capture.utils import RenameSet) 
to avoid having to install pyuvc (this caused problems when installing, and isn't needed for this script to work)

Update methods does not appear to exist in current version of pupil_src?  May need to use legacy?  Could just include in repo??
  
'"""

# set paths (cluster)
#pupilSourcePath = '/data/DATA_ANALYSIS/BOSS_PREPROCESSING/EYE/pupil/pupil_src/shared_modules' # location of pupil_src files
#recording_path = ['/data/DATA_ANALYSIS/BOSS_PREPROCESSING/EYE/Pupil_Labs_For_Export_PF'] # recordings you want to export
#out_dir = '/data/DATA_ANALYSIS/BOSS_PREPROCESSING/EYE/Pupil_Labs_Exported_PF' # exported .csv files destination folder


# set paths (local machine)
import os
scriptsDir = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Pupil_Labs_Batch_Export/batchExport'
os.chdir(scriptsDir)
pupilSourcePath = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/pupil/pupil_src/shared_modules'
#pupilSourcePath = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/pupil_latest_src/pupil_src/shared_modules/pupil_recording'
#pupilSourcePath2 = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/pupil_latest_src/pupil_src/shared_modules'

recording_path = ['/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Example_Files_PY']
out_dir = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Pupil_Labs_Exported'

# export annotations
annotations = True
#surfaces = True

import extract_data
import sys
sys.path.insert(0,pupilSourcePath)
#sys.path.insert(0,pupilSourcePath2)

from update_methods import *

# try importing "rtSurface2"
#from extract_surface import *

import file_methods as fm
import numpy as np
import pandas as pd
import shutil
import pathlib



#from video_capture import *
#from update import new_style

# DEFINE SOME FUNCTIONS FOR SURFACE EXTRACTION
def extract_surface_data(directory):
    surfaces = fm.load_pldata_file(directory, "surfaces")
    surfaces = pd.DataFrame(surfaces, index=surfaces._fields).T
    surfaces.set_index("timestamps", inplace=True)
    for name, surface in surfaces.groupby("topics"):
        export_gaze_positions_on_surface(
            directory,
            name.replace("surfaces.", ""),
            surface.data
        )

def export_gaze_positions_on_surface(directory, name, surface):
    print(f"Extracting {name} data...")
    directory = pathlib.Path(directory)
    surface = surface.transform(select_gaze)
    surface = surface.explode()
    surface = surface.transform(extract_export_data, surface_name=name)
    surface.index.name = "world_timestamps"

    world_ts = np.load(directory / "world_timestamps.npy")
    world_idc = np.searchsorted(world_ts, surface.index)
    surface.insert(0, "world_index", world_idc)
    
    csv_path = directory / f"gaze_positions_on_surface{name}.csv"
    surface.to_csv(csv_path)
    print(f"Exported {surface.shape[0]} gaze positions to {csv_path}")

def select_gaze(surface_datum):
    return surface_datum["gaze_on_srf"]

def extract_export_data(gaze_datum, *, surface_name):
    export_data = pd.Series(
        [
            gaze_datum["timestamp"],
            *gaze_datum["norm_pos"],
            *gaze_datum["norm_pos"],  # for scaling
            gaze_datum["on_srf"],
            gaze_datum["confidence"],
        ],
        index=(
            "gaze_timestamp",
            "x_norm",
            "y_norm",
            "x_scaled",
            "y_scaled",
            "on_surf",
            "confidence",
        )
    )
    export_data.loc["x_scaled"] *= surface_defs[surface_name]["x"]
    export_data.loc["y_scaled"] *= surface_defs[surface_name]["y"]
    return export_data


# START LOOP
recording_valid = []
csv_out = []

for pa in recording_path:
    recording_dates = os.listdir(pa)
    
    # edit for unix compatibility
    if '.DS_Store' in recording_dates:
        recording_dates.remove('.DS_Store')
    
    for da in recording_dates:
        folder = os.path.join(pa, da)
    
        # Find all dates where there was a recording
        recording_sessions = os.listdir(folder)
        
        # edit for unix compatibility
        if '.DS_Store' in recording_sessions:
            recording_sessions.remove('.DS_Store')
        
        for se in recording_sessions:
            # Find all recordings for each day
            session = os.path.join(folder, se)
            
            #add update methods here with session
            update_recording_to_recent(session)  
            
            # grab various data from pupil files
            if os.path.isdir(session):
                
                #breakpoint()
                
                recording_valid.append(session)
                csv_out.append('pupil_positions_'+ da + '_' + se + '.csv')

                if annotations:
                    csv_out.append('annotations_' + da + '_' + se + '.csv')
                    
                    
                    
                # add surfaces export
                try:
                    surface_defs = fm.load_object(os.path.join(session,"surface_definitions"))
                    surface_defs = {srf["name"]: srf["real_world_size"] for srf in surface_defs["realtime_square_marker_surfaces"]}
                    directory = session
                    extract_surface_data(session)
                    out_dir = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Pupil_Labs_Exported'
                    recSession = session[-3:]
                    recFolder = session[-21:-4]
                    srcFile = os.path.join(session,"gaze_positions_on_surfaceBOSS_WEST_SCREEN.csv")
                    destFile = os.path.join(out_dir,'surface_' + recFolder + '_' + recSession + '.csv')
                    shutil.copy(srcFile,destFile)
                    print("Surface Data Extracted!")
                except:
                    print("Surface Data NOT Extracted!")
    
try:                
    extract_data.main(recording_valid, csv_out, out_dir, overwrite = True, annotations = annotations)
except:
    print('Pupil and Annotation Extraction Failed!')




