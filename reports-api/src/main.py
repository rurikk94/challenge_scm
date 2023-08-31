from fastapi import FastAPI


from src.v1.routes import v1

app = FastAPI()

app.include_router(v1, prefix="/v1")
