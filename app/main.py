import os

from typing import Union

from fastapi import BackgroundTasks, FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse

app = FastAPI()

from app.utils import generate_uuid, delete_file, get_model_artefact_filepath

from app.constants import (
    KUBECTL_PATH, OUTPUT_PREFIX, POD_NAME_PREFIX, API_DATA_FOLDER,
    DEFAULT_MODEL_RUN_ID, )

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

@app.post("/async-score")
async def async_score(request: Request):
    call_uuid = generate_uuid()
    response =  JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
                "call_uuid"   : call_uuid,
                "call_status" : "not implemented"
                }
    )

    return response

@app.get("/get-status")
async def get_status(call_uuid):
    response = PlainTextResponse(
        status_code=status.HTTP_200_OK,
        content={
            "call_uuid": call_uuid,
            "call_status": "not implemented"
        }
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