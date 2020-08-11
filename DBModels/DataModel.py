import pymongo
from pymongo import MongoClient

class DataModel:
    def __init__(self, dbName):
        self.client = MongoClient('localhost')
        self.db   = self.client[dbName]

    def getData(
        self,
        collectionName ,
        condition = {},
        returnColumn = None,
        sort={},
        countYN='N',
        mDocs='N'
    ):
        Collection = self.db[collectionName]
        if countYN == 'Y':
            if condition == None:
                result = Collection.count_documents()
            else:
                result = Collection.count_documents(condition)
        else:
            if mDocs == 'N':
                if returnColumn == None:
                    result = Collection.find_one(condition, sort=sort)
                else:
                    result = Collection.find_one(condition,returnColumn,sort=sort)
            else:
                if returnColumn == None:
                    result = Collection.find(condition)
                else:
                    result = Collection.find(condition,projection = returnColumn)

        return result

    def deleteData(self, collectionName, searchCondition, mDocs='N'):
       Collection = self.db[collectionName]
       if mDocs == 'N':
           result = Collection.delete_one(searchCondition)
       else:
           result = Collection.delete_many(searchCondition)
       return result.deleted_count

    def addData(self, collectionName, dataSet, mDocs='N'):
        Collection = self.db[collectionName]
        if mDocs == 'N':
            result = Collection.insert_one(dataSet)
        return result

    def replaceData(self, collectionName, searchCondition, dataSet, isUpsert=True):
        Collection = self.db[collectionName]
        result = Collection.replace_one(searchCondition, dataSet, isUpsert)
        return result

    def updateData(self, collectionName, searchCondition, dataSet, updateType, isUpsert=False):
        Collection = self.db[collectionName]
        if updateType == 'PUSH':
            setCommand = { "$push" :  dataSet }
        else:
            setCommand = { "$set" : dataSet}
        result = Collection.update_one(searchCondition, setCommand)
        return result
