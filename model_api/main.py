import uvicorn
from fastapi import FastAPI, Request
from model_api.lib.lib import Database

from model_api.model import InferenceModel
from config import MONGODB_URL

db = Database(db_name='main', mongodb_url=MONGODB_URL)
app = FastAPI()
inference = InferenceModel("models/full_model_epoch_10.pt")


@app.post("/predict")
async def classify(request: Request):
    form = await request.form()
    text = form.get('text')

    doc_type = db.get_doc_type(text)
    if doc_type:
        return doc_type

    doc_type = inference.predict(text)
    db.save_doc(text, doc_type)

    return doc_type

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
