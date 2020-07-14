import pymongo
from pymongo import MongoClient

class DataModel:
    def __init__(self, dbName):
        self.client = MongoClient('localhost')
        self.db   = self.client[dbName]

    def getOneData(self, collectionName, condition, countYN='N'):
        Collection = self.db[collectionName]
        if countYN == 'Y':
            result = Collection.count_documents(condition)
        else:
            result = Collection.find_one(condition)

        return result

    def addData(self, collectionName, insertData, mRows='N'):
        Collection = self.db[collectionName]
        print(Collection)
        print(insertData)
        if mRows == 'N':
            result = Collection.insert_one(insertData).inserted_id
            return result
