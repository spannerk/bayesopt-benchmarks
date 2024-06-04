from typing import Union

from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}

def write_file(file_id: int):
    with open("{}.txt".format(file_id), mode="w") as f:
        content = f"hi"
        f.write(content)


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/makefile/{file_id}")
async def make_a_file(file_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_file, file_id)
    return {"message": "{} started".format(file_id)}