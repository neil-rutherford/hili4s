from flask import Blueprint

bp = Blueprint('acct', __name__)

from app.acct import routes