from typing import Dict, List

from pymongo import MongoClient


class MongoDB:
    def __init__(self, host: str, port: str, db_name: str, user: str, password: str):
        uri = f'mongodb://{user}:{password}@{host}:{port}/'
        client = MongoClient(uri)
        self.__db = client[db_name]

    def insert(self, coll_name: str, data: Dict):
        coll = self.__db[coll_name]
        r = coll.insert_one(data)

        print(f'Data inserted: {r.inserted_id}')

    def get(self, coll_name: str, query: Dict):
        coll = self.__db[coll_name]
        docs = coll.find()

        return docs

    def list_coll(self) -> List:
        return self.__db.list_collection_names()

