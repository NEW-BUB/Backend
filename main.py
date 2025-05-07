from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def main():
    return ""

@app.get("/hello")
def hello():
    return {"message": "hello world"}