import json
import bleach
from bukget.api.db import db
from bottle import Bottle

app = Bottle()