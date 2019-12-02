# batchExportPupilLabs

Original Authors: Py and Papr (adapted, badly, by TB )
Date: 12.01.19

Disclamer: This repo is a mess, but the scripts do work.  I will eventually clean it up.

## Purpose

Loop through recordings in a specifed directory
Update recording format if recorded in legacy format
Export data to .csv files in a specified directory

## Instructions

Edit the directory paths in `Batch_Export.py` and run

## Notes

Requires modules from an older version of pupil_src (see pupil folder included in this repo)

Runs in python 3.x

Needs numpy, scipy, pandas, shutil, os, sys, etc.

Needs av: conda install -c conda-forge av

Needs cv: conda install-c conda-forge opencv

Needs msgpack 0.5.6 (latest version [6] breaks the export): conda install -c anaconda msgpack-python=0.5.6

Needs modules from pupil/pupil_src/shared modules (git clone https://github.com/pupil-labs/pupil)

IMPORTANT: I had to comment out line 26 in "update_methods.py" [from video_capture.utils import RenameSet]
to avoid having to install pyuvc (this caused problems when installing, and isn't needed for this batch export script to work)


