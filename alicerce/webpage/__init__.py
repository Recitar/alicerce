from flask import Blueprint
from alicerce.webpage.views import index, reply_answer, start_session

site_bp = Blueprint("chatbot", __name__, template_folder="templates")

site_bp.add_url_rule("/", view_func=index, endpoint="index")
site_bp.add_url_rule("/index", view_func=index, endpoint="index")
site_bp.add_url_rule("/answer", view_func=reply_answer, endpoint="get_answer")
site_bp.add_url_rule("/startSession", view_func=start_session)