# batchExportPupilLabs

Authors: Py (adapted by TB to work with unix and legacy files) 
Date: March 2019

## Purpose

Loop through recordings in a specified directory
Update to latest version of recording format (if recorded in legacy format)
Export data to .csv files 

## Instructions

Edit the directory paths in `folderwalk.py` and run

## Notes

Runs in python 3.x

Needs numpy, scipy

Needs av: conda install -c conda-forge av

Needs cv: conda install-c conda-forge opencv

Needs msgpack 0.5.6 (latest version [6] breaks the export): conda install -c anaconda msgpack-python=0.5.6

Needs modules from pupil/pupil_src/shared modules (git clone https://github.com/pupil-labs/pupil)

IMPORTANT: I had to comment out line 26 in "update_methods.py" [from video_capture.utils import RenameSet]
to avoid having to install pyuvc (this caused problems when installing, and isn't needed for this batch export script to work)


## TO DO

Figure out how to export surface gaze data (currently only exports annotations and pupil data)
 