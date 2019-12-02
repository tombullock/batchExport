#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 19:43:06 2019

@author: tombullock

CURRENTLY ONLY WORKS IF EXPORTED VIA THE GUI (MORE RECENT PUPIL LABS)


Really just need to set up folderwalk (see batch_export script) and loop through all dirs!

## MUST RENAME FOLDERS FIRST!!!

Why is this only working for my file that I uploaded to dropbox?  Something to do wtih src?  If I get a clean file and export using my other code, will it work?  Or do i need to update in gui (new code?)
"""

import pathlib
import sys
sys.path.append('/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/pupil/pupil_src/shared_modules')
#sys.path.append('/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/pupil_latest_src/pupil_src/shared_modules')
import file_methods as fm
import numpy as np
import pandas as pd
import os
import shutil

# test data dir

#directory = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Example_Files_PY/BOSS_206_2_1_1_g1/000'

#directory = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Example_Files_PY/b''BOSS_206_2_1_1_g5'''


# define surfaces
#surface_defs = fm.load_object("surface_definitions")
#surface_defs = {srf["name"]: srf["real_world_size"] for srf in surface_defs["surfaces"]}

# WORKS
#surface_defs = fm.load_object(os.path.join(directory,"surface_definitions"))
#surface_defs = {srf["name"]: srf["real_world_size"] for srf in surface_defs["realtime_square_marker_surfaces"]}
#out_dir = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Pupil_Labs_Exported'





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


##extract_surface_data(".")
#extract_surface_data(directory)



#recSession = directory[-3:]
#recFolder = directory[-21:-4]



#destFile = os.path.join(out_dir, 'sj' + sjNum + '_se0' + iSession + '_' + task + '.csv')

#srcFile = os.path.join(directory,"gaze_positions_on_surfaceBOSS_WEST_SCREEN.csv")
#destFile = os.path.join(out_dir,'surface_' + recFolder + '_' + recSession + '.csv')
#shutil.copy(srcFile,destFile)


