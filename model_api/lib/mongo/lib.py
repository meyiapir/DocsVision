from model_api.lib.mongo.client import Client
from model_api.lib.hash import text_to_hash


class Database(Client):
    def save_doc(self, text: str, doc_type: str):
        self.insert('documents', {'hash': text_to_hash(text), 'doc_type': doc_type})

    def get_doc_type(self, text: str):
        r = self.find('documents', {'hash': text_to_hash(text)})
        if r:
            return r[0]['doc_type']
        return None