import requests

BASE_URL = "https://www.beeminder.com/api/v1/"

class Beeminder:
    def __init__(self, username, auth_token):
        self.url = f"{BASE_URL}users/{username}"
        self.auth_token = auth_token
    
    def make_params(self):
        return {
            "auth_token": self.auth_token,
        }

    def create_datapoint(self, goal: str, value: float, timestamp: float = None, daystamp: str = None, comment: str = None, requestid: str = None):
        url = f"{self.url}/goals/{goal}/datapoints.json"
        data = locals()
        data.pop("goal")
        params = self.make_params()
        return requests.post(url, data=data, params=params)
