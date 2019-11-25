import argparse
import csv
import logging
import os
import traceback as tb

import numpy as np
import msgpack
import sys

logger = logging.getLogger(__name__)

def main(recordings, csv_out, out_directory = '', overwrite=False, annotations = True, surfaces=True):
    """Process given recordings one by one

    Iterates over each recording and handles cases where no pupil.pldata or
    pupil_timestamps.npy files could be found.

    recordings: List of recording folders
    csv_out: CSV file name under which the result will be saved
    """
    idx = 0
    for rec in recordings:
        try:
            logger.info("Extracting {}...".format(rec))
            
            #pm.update_recording_to_recent(rec)
            process_recording(rec, csv_out[idx], out_directory, overwrite=overwrite)
            

            if annotations:
                process_recording_annotations(rec, csv_out[idx+1], out_directory, overwrite=overwrite)
                
            # process surface recording (TOM ADDED!!!)
            if surfaces:
                process_recording_surface(rec, csv_out[idx+2], out_directory, overwrite=overwrite)
                

        except FileNotFoundError:
            logger.warning(
                (
                    "The recording {} did not include any prerecorded pupil files!"
                ).format(rec)
            )
            logger.debug(tb.format_exc())
        except ValueError:
            logger.warning(rec)
            
        if annotations and surfaces:
            idx +=3
        else:
            idx +=2 # annotations only
            
#        if annotations:
#            idx += 2 # original 
#        else:
#            idx += 1
            
            
            
            
    return



def process_recording(recording, csv_out, out_directory, overwrite=False):
    """Process a single recording

    recordings: List of recording folders
    csv_out: CSV file name under which the result will be saved
    overwrite: Boolean indicating if an existing csv file should be overwritten
    """
    if len(out_directory) == 0:
        csv_out_path = os.path.join(recording, csv_out)
    else:
        csv_out_path = os.path.join(out_directory, csv_out)

    if os.path.exists(csv_out_path):
        if not overwrite:
            logger.warning("{} exists already! Not overwriting.".format(csv_out_path))
            return
        else:
            logger.warning("{} exists already! Overwriting.".format(csv_out_path))

    with open(csv_out_path, "w", newline = '') as csv_file:
        writer = csv.writer(csv_file, dialect=csv.get_dialect('excel'))
        writer.writerow(csv_header())

        extracted_rows = load_and_yield_data(recording)
        writer.writerows(extracted_rows)
    return

def process_recording_annotations(recording, csv_out, out_directory, overwrite=False):
    """Process a single recording

    recordings: List of recording folders
    csv_out: CSV file name under which the result will be saved
    overwrite: Boolean indicating if an existing csv file should be overwritten
    """
    if len(out_directory) == 0:
        csv_out_path = os.path.join(recording, csv_out)
    else:
        csv_out_path = os.path.join(out_directory, csv_out)

    if os.path.exists(csv_out_path):
        if not overwrite:
            logger.warning("{} exists already! Not overwriting.".format(csv_out_path))
            return
        else:
            logger.warning("{} exists already! Overwriting.".format(csv_out_path))

    with open(csv_out_path, "w") as csv_file:
        writer = csv.writer(csv_file, dialect=csv.unix_dialect, quoting = csv.QUOTE_NONE)
        writer.writerow(csv_header_annotations())

        extracted_rows = load_and_yield_annotations(recording)
        writer.writerows(extracted_rows)
    return

def csv_header():
    """CSV header fields"""
    return (
        "eye_id",
        "timestamp",
        "confidence",
        "diameter",
        "diameter_3d",
    )

def csv_header_annotations():
    """CSV header fields"""
    return (
        "timestamp",
        "label"
    )

def load_and_yield_annotations(directory, topic = 'notify'):
    try:
        ts_file = os.path.join(directory, topic + "_timestamps.npy")
        data_ts = np.load(ts_file)

        msgpack_file = os.path.join(directory, topic + ".pldata")
        with open(msgpack_file, "rb") as fh:
            unpacker = msgpack.Unpacker(fh, raw=False, use_list=False)
            for timestamp, (topic, payload) in zip(data_ts, unpacker):
                datum = deserialize_msgpack(payload)
                label = extract_eyeid_messages(datum)
                yield(timestamp, label)
    except FileNotFoundError:
        logger.warning("{} cannot be processed - file does not exist".format(ts_file))
        logger.warning("Creating fake annotations")

    return

def load_and_yield_data(directory, topic="pupil"):
    """Load and extract pupil diameter data

    See the data format documentation[2] for details on the data structure.

    Adapted open-source code from Pupil Player[1] to read pldata files.
    Removed the usage of Serialized_Dicts since this script has the sole purpose
    of running through the data once.

    [1] https://github.com/pupil-labs/pupil/blob/master/pupil_src/shared_modules/file_methods.py#L137-L153
    [2] https://docs.pupil-labs.com/#data-files
    """
    try:
        ts_file = os.path.join(directory, topic + "_timestamps.npy")
        data_ts = np.load(ts_file)

        msgpack_file = os.path.join(directory, topic + ".pldata")
        with open(msgpack_file, "rb") as fh:
            unpacker = msgpack.Unpacker(fh, raw=False, use_list=False)
            for timestamp, (topic, payload) in zip(data_ts, unpacker):
                datum = deserialize_msgpack(payload)

                # custom extraction function for pupil data, see below for details
                eye_id, conf, dia_2d, dia_3d = extract_eyeid_diameters(datum)
                # yield data according to csv_header() sequence
                yield (eye_id, timestamp, conf, dia_2d, dia_3d)
    except FileNotFoundError:
        logger.warning("{} cannot be processed - file does not exist".format(ts_file))
        return
    return 




######### TOM ADD SURFACES ###########
    
def load_and_yield_surfaces(directory, topic="surfaces"):

    try:
        ts_file = os.path.join(directory, topic + "_timestamps.npy")
        data_ts = np.load(ts_file)

        msgpack_file = os.path.join(directory, topic + ".pldata")
        with open(msgpack_file, "rb") as fh:
            unpacker = msgpack.Unpacker(fh, raw=False, use_list=False)
            for timestamp, (topic, payload) in zip(data_ts, unpacker):
                datum = deserialize_msgpack(payload)

                #breakpoint()
               
                # custom function for extract surface data, see below for details
                on_srf, s_xNormPos, s_yNormPos = extract_surface_data(datum)
                
                # yield data according to csv_header() sequence
                yield (timestamp, s_xNormPos, s_yNormPos, on_srf)
                
    except FileNotFoundError:
        logger.warning("{} cannot be processed - file does not exist".format(ts_file))
        return
    return 


def extract_surface_data(surface_datum):
    """Extract data from surface...
    """
    #print(surface_datum)
    #print(surface_datum['gaze_on_srf'][0]['on_srf'])

    return (
        #surface_datum["id"],
        #surface_datum["confidence"],
        #surface_datum["diameter"],
        #surface_datum['gaze_on_srf'][0]['timestamp'],
        #surface_datum['timestamp'],  
        
        surface_datum['gaze_on_srf'][0]['on_srf'],
        surface_datum['gaze_on_srf'][0]['norm_pos'][0], # x coord
        surface_datum['gaze_on_srf'][0]['norm_pos'][1] # y coord
    )


def csv_header_surface():
    """CSV header fields"""
    return (
        #"s_eye_id",
        #"timestamp",
        #"s_confidence",
        #"s_diameter",
        "s_timestamp",
        "s_xNormPos",
        "s_yNormPos",
        "on_srf",
    )
    
    
def process_recording_surface(recording, csv_out, out_directory, overwrite=False):
    """Process a single recording

    recordings: List of recording folders
    csv_out: CSV file name under which the result will be saved
    overwrite: Boolean indicating if an existing csv file should be overwritten
    """
    if len(out_directory) == 0:
        csv_out_path = os.path.join(recording, csv_out)
    else:
        csv_out_path = os.path.join(out_directory, csv_out)

    if os.path.exists(csv_out_path):
        if not overwrite:
            logger.warning("{} exists already! Not overwriting.".format(csv_out_path))
            return
        else:
            logger.warning("{} exists already! Overwriting.".format(csv_out_path))

    with open(csv_out_path, "w", newline = '') as csv_file:
        writer = csv.writer(csv_file, dialect=csv.get_dialect('excel'))
        writer.writerow(csv_header_surface())

        extracted_rows = load_and_yield_surfaces(recording)
        writer.writerows(extracted_rows)
    return


####### END TOM ADD SURFACES #######





def extract_eyeid_diameters(pupil_datum):
    """Extract data for a given pupil datum
    
    Returns: tuple(eye_id, confidence, diameter_2d, and diameter_3d)
    """
    return (
        pupil_datum["id"],
        pupil_datum["confidence"],
        pupil_datum["diameter"],
        pupil_datum.get("diameter_3d", 0.0)
    )

def extract_eyeid_messages(datum):
    """Extract data for a given pupil datum
    
    Returns: tuple(eye_id, confidence, diameter_2d, and diameter_3d)
    """
    return (
        datum.get("label", '')
    )


def deserialize_msgpack(msgpack_bytes):
    """Deserialize msgpack[1] data

    [1] https://msgpack.org/index.html
    """
    return msgpack.unpackb(msgpack_bytes, raw=False, use_list=False)

if __name__ == "__main__":
    # setup logging
    logging.basicConfig(level=logging.DEBUG)

    # setup command line interface
    parser = argparse.ArgumentParser(
        description=(
            "Extract 2d and 3d (if available) "
            "pupil diameters for a set of given recordings. "
            "The resulting csv file will be saved within its "
            "according recording."
        )
    )
    parser.add_argument(
        "--recordings", 
        nargs="+", 
        help="One or more recordings"
    )

    parser.add_argument(
        "--out",
        nargs = '+',
        help="CSV file name containing the extracted data",
        default="pupil_positions.csv",
    )

    parser.add_argument(
        "--dir",
        help="CSV file name containing the extracted data",
        default='',
    )

    parser.add_argument(
        "-f",
        "--overwrite",
        action="store_true",
        help=(
            "Usually, the command refuses to overwrite existing csv files. "
            "This flag disables these checks."
        ),
    )

    parser.add_argument(
        "-a",
        "--annotations",
        action="store_false",
        help=(
            "Usually you want to also extract the annotations"
            "This flag disables this."
        ),
    )
    
    # parse command line arguments and start the main procedure
    args = parser.parse_args()
    main(recordings=args.recordings, csv_out=args.out, out_directory = args.dir, overwrite=args.overwrite)
