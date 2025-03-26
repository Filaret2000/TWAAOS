from fastapi import FastAPI

app = FastAPI()

@app.get("/fastapi-api/hello")
async def hello():
    return {"message": "Hello from FastAPI!"}
