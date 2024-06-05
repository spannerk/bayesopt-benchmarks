'''
Helper module with utility functions taken from WSM Python API.
'''

# System imports
import os
import random
import time
import string
from abc import ABC, abstractmethod
from os.path import join


from constants import API_DATA_FOLDER, INPUT_JSON_PREFIX, OUTPUT_PREFIX, POD_SPEC_PREFIX

class InitScoringException(Exception):
    '''
    Raised when there is an issue with the initialisation of the async-score endpoint
    '''

def delete_file(filename, log_call_uuid=None):
    '''
    Deletes a file from the filesystem and logs the details of the operation
    against an optional run uuid.

    Parameters
    ----------
    filename : string
        Filename of the file to delete, including path relative to the app root
    log_call_uuid : string, optional
        If call_uuid is provided, it's added to the logs. By default None

    Returns
    -------
    None
    '''

    message = f"Attempting to remove {filename}"


    try:
        os.remove(filename)
        message = f"Removed {filename}"

    except FileNotFoundError:
        message = f"{filename} not found. Nothing to remove."


def write_to_file(input_data, filename, log_call_uuid=None):
    '''
    Writes data to file and logs the details of the operation
    against an optional run uuid.

    Parameters
    ----------
    input_data : string
        Data to be written to file
    filename : string
        Filename, including path relative to the app root
    log_call_uuid : string, optional
        If call_uuid is provided, it's added to the logs. By default None

    Returns
    -------
    None
    '''

    # message = f"Attempting to write {filename}"
    # try:
    #     with open(filename, "w", encoding="utf-8") as f:
    #         f.write(input_data)
    # except:
    #     message = f"Could not write to {filename}."

    with open(filename, "w", encoding="utf-8") as f:
        f.write(input_data)

def generate_uuid():
    '''
    Generate a UUID based on random digits (instead of the hardware address), 
    plus the current time. 

    Note that the uuid generated by this function might not be the final uuid of
    the API invocation - if model run id is present in the input JSON, it will be
    appended to this UUID during initialisation.

    Returns
    ------
    UUID string to allow us to include the UUID in the response JSON.
    '''

    formatted_time = time.strftime("%Y-%m-%d-%H-%M-%S" , time.gmtime())
    run_id = "wsm-" + formatted_time + "-" + "".join(random.choices(string.ascii_lowercase, k=5))

    return run_id

def get_model_artefact_filepath(call_uuid, artefact_type):
    '''
    Get the absolute path to the specified model artefact.

    Parameters
    ----------
    call_uuid     : str
        API invocation ID provides a unique identifier in the filepath to model artefacts.
    artefact_type : str
        The type of model artefact, like input JSON or output CSV. Supported value are:
        "model_input", "model_output", "model_pod_spec".
    
    Returns
    ----------
    Filepath string
    '''

    known_artefact_types = ["model_input", "model_output", "model_pod_spec"]

    if artefact_type not in known_artefact_types:
        msg = f"Can't generate filepath for {artefact_type}. Supported values are: {', '.join(known_artefact_types)}"
        raise ValueError(msg)

    path_dict = {
        "model_input"    : join(API_DATA_FOLDER, call_uuid, "inputs", f"{INPUT_JSON_PREFIX}{call_uuid}.json"),
        "model_output"   : join(API_DATA_FOLDER, call_uuid, "results", f"{OUTPUT_PREFIX}{call_uuid}.csv"),
        "model_pod_spec" : join(API_DATA_FOLDER, call_uuid, "inputs", f"{POD_SPEC_PREFIX}{call_uuid}.json"),
    }

    return path_dict[artefact_type]