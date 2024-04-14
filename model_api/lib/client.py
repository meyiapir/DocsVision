from pymongo import MongoClient


class Client:
    def __init__(self, db_name, mongodb_url):
        self.db_name = db_name
        self.client = MongoClient(mongodb_url)

    def insert(self, collection_name, data: list[dict] | dict):
        collection_name = self.client[self.db_name][collection_name]
        if isinstance(data, dict):
            r = collection_name.insert_one(data)
        elif isinstance(data, list):
            r = collection_name.insert_many(data)
        print(r)

    def find(self, collection_name: str, filter: dict = {}):
        return list(self.client[self.db_name][collection_name].find(filter))

    def delete(self, collection_name: str, data: list[dict] | dict):
        collection_name = self.client[self.db_name][collection_name]
        if isinstance(data, list) or data == {}:
            r = collection_name.delete_many(data)
        elif isinstance(data, dict):
            r = collection_name.delete_one(data)
