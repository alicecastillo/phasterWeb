
class PhasterJSON:
    def __init__(self, jsonData):
        self.job_id = jsonData["job_id"]
        self.status = jsonData["status"]
        self.url = jsonData["url"]
        self.zip = jsonData["zip"]
        self.summary = jsonData["summary"] 
    def __eq__(self, other):
        return self.job_id==other.job_id
    def __hash__(self):
        return hash(('job_id', self.job_id))