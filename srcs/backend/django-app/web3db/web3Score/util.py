import json
import os

class JsonFile():
    def __init__(self, path) -> None:
        self.filepath = path
        self.data = {}
    
    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, data):
        self.data[key] = data

    def save(self):
        if self.data is None:
            return
        jsonFile = open(self.filepath, "w")
        jsonFile.write(json.dumps(self.data))
        jsonFile.close()

    def load(self):
        jsonFile = open(self.filepath)
        self.data = json.load(jsonFile)
        jsonFile.close() 
        return self.data

    def fileExists(self):
        return os.path.isfile(self.filepath)