""" 
Authors: Py (adapted by TB to work with unix and legacy files) 
Date: March 2019 (updated Nov 24th 2019)

Purpose: 
Loop through recordings in a specified directory
Update to latest version of recording format (if recorded in legacy format)
Export data to .csv files 

Notes: 
Runs in python 3.x
Needs numpy, scipy
Needs av: conda install -c conda-forge av
Needs cv: conda install-c conda-forge opencv
Needs msgpack 0.5.6 (latest version [6] breaks the export): conda install -c anaconda msgpack-python=0.5.6  # possibly anaconda3? 
Needs modules from pupil/pupil_src/shared modules (git clone https://github.com/pupil-labs/pupil)
IMPORTANT: I had to comment out line 26 in "update_methods.py" (from video_capture.utils import RenameSet) 
to avoid having to install pyuvc (this caused problems when installing, and isn't needed for this script to work)

To dos: 
    
Figure out how to export ALL data (gaze, surface etc).  Currently only exports annotations and pupil diameter data.     
    

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
recording_path = ['/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Example_Files']
out_dir = '/Users/tombullock/Documents/Psychology/BOSS_Local/Pupil_Labs_Development/Pupil_Labs_Exported'

# export annotations
annotations = True
surfaces = True

import extract_diameter
import sys
sys.path.insert(0,pupilSourcePath)
from update_methods import *

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
                recording_valid.append(session)
                csv_out.append('pupil_positions_'+ da + '_' + se + '.csv')

                if annotations:
                    csv_out.append('annotations_' + da + '_' + se + '.csv')
                    
                if surfaces:
                    csv_out.append('surfaces_' + da + '_' + se + '.csv') # not working
                                        

extract_diameter.main(recording_valid, csv_out, out_dir, overwrite = True, annotations = annotations, surfaces = surfaces)



