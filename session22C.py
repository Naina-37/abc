from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class MongoDBHelper:
    def __init__(self, collection="appusers"):
        # MongoDB connection string
        uri = "mongodb+srv://nainagupta9914:1234@cluster0.xmcswke.mongodb.net/?appName=Cluster0"

        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
        
        # Select the database and collection
        self.db = self.client['gw2810']
        self.collection = self.db[collection]

    # Insert a document into the collection
    def insert(self, document, collection_name=None):
        try:
            if collection_name:
                collection = self.db[collection_name]
            else:
                collection = self.collection
            result = collection.insert_one(document)
            print(f"Document inserted in Collection: {collection.name}")
            print("Result:", result)
            return result
        except Exception as e:
            print(f"Error inserting document: {e}")
            return None

    # Fetch documents based on a query
    def fetch(self, query=None, collection_name=None):
        if query is None:
            query = {}
        try:
            if collection_name:
                collection = self.db[collection_name]
            else:
                collection = self.collection
            print(f"Fetching from collection: {collection.name} with query: {query}")
            documents = collection.find(query)
            documents_list = list(documents) if documents else []
            print(f"Found documents: {documents_list}")
            return documents_list
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []

    # Delete a document based on the query
    def delete_one(self, query, collection_name=None):
        try:
            if collection_name:
                collection = self.db[collection_name]
            else:
                collection = self.collection
            print(f"Deleting from collection: {collection.name} with query: {query}")
            result = collection.delete_one(query)
            print(f"Deleted {result.deleted_count} document(s)")
            return result
        except Exception as e:
            print(f"Error deleting document: {e}")
            return None

    # Update a document based on a query and document data
    def update(self, query, update_data, collection_name=None):
        try:
            if collection_name:
                collection = self.db[collection_name]
            else:
                collection = self.collection
            print(f"Updating collection: {collection.name} with query: {query} and data: {update_data}")
            update_query = {'$set': update_data}
            result = collection.update_one(query, update_query)
            print(f"Updated {result.modified_count} document(s)")
            return result
        except Exception as e:
            print(f"Error updating document: {e}")
            return None

    # Search for devices based on device_name, device_type, and status
    def search_devices(self, device_name=None, device_type=None, status=None):
        search_query = {}

        if device_name:
            search_query['device_name'] = {"$regex": device_name, "$options": "i"}  # Case-insensitive search for device_name
        if device_type:
            search_query['device_type'] = {"$regex": device_type, "$options": "i"}  # Case-insensitive search for device_type
        if status:
            search_query['status'] = status  # Search for exact status match

        print(f"Searching for devices with query: {search_query}")
        try:
            devices = self.collection.find(search_query)
            devices_list = list(devices) if devices else []
            print(f"Found devices: {devices_list}")
            return devices_list
        except Exception as e:
            print(f"Error searching for devices: {e}")
            return []

