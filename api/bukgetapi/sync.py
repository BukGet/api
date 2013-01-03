import json
import bleach
from bottle import Bottle, redirect, response, request

app = Bottle()

@app.hook('before_request')
def set_json_header():
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')