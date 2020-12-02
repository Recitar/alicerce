from flask import current_app, render_template, request, make_response


from alicerce.webpage.business import (
    process_answer_request, process_start_session
)


def index():
    return render_template("index.html", title='SucupiraBot', page="chatbot")


def reply_answer():
    current_app.logger.debug("Entrei na funcao reply_answer")
    msg = request.args.get("msg")
    if msg:
        return process_answer_request(sentence=msg)


def start_session():
    return process_start_session()


