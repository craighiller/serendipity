import json

def config():
    s = """{
    "client_id": "57b06bf781d28bb",
    "secret": "05e2806b44ca2a66452156926c6144bb77af22fd",
    "token_store": {}
    }"""
    return json.loads(s)