import uvicorn
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()


@app.get("/classify")
async def classify(text: str):
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)
