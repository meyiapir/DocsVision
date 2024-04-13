import uvicorn
from fastapi import FastAPI, Request, HTTPException

from model_api.lib.mongo.lib import Database

db = Database('main')
app = FastAPI()


@app.get("/classify")
async def classify(text: str):
    doc_type = db.get_doc_type(text)
    if doc_type:
        return doc_type

    '''
    model
    '''

    doc_type = 'proxy'
    db.save_doc(text, doc_type)

    return doc_type

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)
