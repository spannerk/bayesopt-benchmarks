import os
import time
from typing import Union

from fastapi import BackgroundTasks, FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from pydantic import BaseModel

from utils import generate_uuid, delete_file, get_model_artefact_filepath, write_to_file
from constants import (
    KUBECTL_PATH, OUTPUT_PREFIX, POD_NAME_PREFIX, API_DATA_FOLDER,
    DEFAULT_MODEL_RUN_ID, )


app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/liveness")
def liveness():
    '''
    Liveness endpoint
    Lightweight endpoint to test whether the API is running and processing requests
    '''
    return "API is live"

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/async-score")
async def async_score(item: Item, background_tasks: BackgroundTasks):
    call_uuid = generate_uuid()
    background_tasks.add_task(process_function, call_uuid, item)
    response =  JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
                "call_uuid"   : call_uuid,
                "call_status" : "task initialized"
                }
    )

    return response

@app.get("/get-status")
async def get_status(call_uuid):

    model_input_filepath    = get_model_artefact_filepath(call_uuid, "model_input")
    model_output_filepath   = get_model_artefact_filepath(call_uuid, "model_output")
    folder = os.path.join(API_DATA_FOLDER, call_uuid)

    input_exists = os.path.exists(model_input_filepath)
    output_exists = os.path.exists(model_output_filepath)
    folder_exists = os.path.exists(folder)

    if input_exists and output_exists:
        status_val = 'Succeeded'
    elif input_exists:
        status_val = 'Running'
    elif not folder_exists:
        status_val = 'Not Found'
    else:
        status_val = 'Unknown'

    response = PlainTextResponse(
        status_code=status.HTTP_200_OK,
        content=status_val
    )
    return response

@app.get("/get-output")
async def get_model_output(call_uuid, background_tasks: BackgroundTasks, delete_pod_files: bool = True):

    model_input_filepath    = get_model_artefact_filepath(call_uuid, "model_input")
    model_output_filepath   = get_model_artefact_filepath(call_uuid, "model_output")
    model_pod_spec_filepath = get_model_artefact_filepath(call_uuid, "model_pod_spec")

    # check that output_filename exists. FastAPI will be happy to return an empty FileResponse
    if not os.path.exists(model_output_filepath):
        raise HTTPException(status_code=404, detail=f"{model_output_filepath} not found.")
    
    # background tasks will run after the response has been sent; logging is done by delete_file
    if delete_pod_files is True:
        background_tasks.add_task(delete_file, model_input_filepath, call_uuid)
        background_tasks.add_task(delete_file, model_pod_spec_filepath, call_uuid)
        background_tasks.add_task(delete_file, model_output_filepath, call_uuid)

    return FileResponse(model_output_filepath)

async def process_function(call_uuid, item):

    results_path = os.path.join(API_DATA_FOLDER, call_uuid, "results")
    inputs_path = os.path.join(API_DATA_FOLDER, call_uuid, "inputs")
    os.makedirs(results_path)
    os.makedirs(inputs_path)


    model_input_filepath    = get_model_artefact_filepath(call_uuid, "model_input")
    model_output_filepath   = get_model_artefact_filepath(call_uuid, "model_output")

    write_to_file(item.model_dump_json(), model_input_filepath)

    # do some longish process
    time.sleep(30)

    write_to_file(item.model_dump_json(), model_output_filepath)