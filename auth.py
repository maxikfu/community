"""
Here I will read access tokens from txt file for safety
"""
import json


class Token:
    def __init__(self):
        with open('tokens.json', 'r') as f:
            data = json.loads(f.readline())
        self.community = data['comm_token']
        self.user = data['usr_token']
        self.comm_id = -167621445
        self.usr_id = 491551942


if __name__=='__main__':
    t = Token()