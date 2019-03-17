# batchExport

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
