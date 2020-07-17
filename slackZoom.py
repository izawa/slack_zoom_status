import psutil
import time
import os
import requests
import json

class Zoom:
    @classmethod
    def checkZoom(cls):
        x = [p for p in psutil.process_iter() if(p.status() == "running" and p.name() == 'CptHost')]
        return(True if len(x) > 0 else False)

class Slack:
    def __init__(self):
        self.token = os.environ["SLACK_TOKEN"]
        self.user_id = os.environ["SLACK_USER_ID"]
        self.headers = {"Authorization": "Bearer %s" % self.token, "X-Slack-User": self.user_id, "Content-Type": "application/json; charset=utf-8"}

    def set_status(self, status_emoji, status_text):
        payload = {"profile": {"status_emoji": status_emoji, "status_text": status_text}}
        res = requests.post("https://slack.com/api/users.profile.set", data=json.dumps(payload), headers=self.headers).json()

    def get_status(self):
        payload = {}
        res = requests.post("https://slack.com/api/users.profile.get", data=json.dumps(payload), headers=self.headers).json()
        return({'status_emoji' : res['profile']['status_emoji'],
                'status_text' : res['profile']['status_text']})
        
class StateMachine:
    def __init__(self):
        self.stat = False

    def get_state(self):
        return(self.stat)

    def set_state(self, status):
        if (self.stat == status):
            return(False)
        else:
            self.stat = status
            return(True)
    

myMachine = StateMachine()
mySlack = Slack()

while True:
    status = Zoom.checkZoom()
    if(myMachine.set_state(status)):
        if(status):
            prev_status = mySlack.get_status()
            mySlack.set_status(":zoom:", "In a meeting via Zoom")
        else:
            mySlack.set_status(prev_status["status_emoji"], prev_status["status_text"])
    else:
        pass
    time.sleep(3)
