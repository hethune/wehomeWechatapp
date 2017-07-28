from flask import request, jsonify, g
from flask import Blueprint
from index import app, db

mob = Blueprint('mob', __name__)
logger = app.logger