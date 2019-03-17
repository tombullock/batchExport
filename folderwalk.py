""" 
Authors: Py (adapted by TB to work with unix and legacy files) 
Date: March 2019

Purpose: 
Loop through recordings in a specified directory
Update to latest version of recording format (if recorded in legacy format)
Export data to .csv files 

Notes: 
Runs in python 3.x
Needs packages like numpy, av etc.
Needs msgpack 0.5.6 (latest version [6] breaks the export)
Needs files from pupil/pupil_src/shared modules (git clone https://github.com/pupil-labs/pupil)
IMPORTANT: I had to comment out line 26 in "update_methods.py" (from video_capture.utils import RenameSet) 
to avoid having to install pyuvc (this caused problems when installing, and isn't needed for this script to work)

To do: figure out how to export surface gaze data (currently only exports annotations and pupil data)

'"""

# set paths
pupilSourcePath = "/Users/tombullock/Documents/Psychology/BOSS/pupil/pupil_src/shared_modules" # location of pupil src files
recording_path = ['/Users/tombullock/Documents/Psychology/BOSS/PUPIL_TEST_EXPORT'] # recordings you want to export
out_dir = '/Users/tombullock/Documents/Psychology/BOSS/PUPIL_TEST_EXPORTED' # exported .csv files destination folder

# export annotations
annotations = True


import os
import extract_diameter
import sys
sys.path.insert(0,pupilSourcePath)
import update_methods

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

        for se in recording_sessions:
            # Find all recordings for each day
            session = os.path.join(folder, se)
            
            #add update methods here with session
            update_recording_to_recent(session)

            if os.path.isdir(session):
                recording_valid.append(session)
                csv_out.append('pupil_positions_'+ da + '_' + se + '.csv')

                if annotations:
                    csv_out.append('annotations_' + da + '_' + se + '.csv')

extract_diameter.main(recording_valid, csv_out, out_dir, overwrite = True, annotations = annotations)



