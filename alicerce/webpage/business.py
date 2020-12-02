from http import HTTPStatus
from flask import session, jsonify, request
import uuid

from alicerce.bot.iqa import get_answer


def process_answer_request(sentence):
    user_id = session["user_id"]
    answer = "Esta sessão foi expirada. Por favor, reinicie a página atual."
    if user_id:

        chat = session["chat"]

        turn = {
            "user": sentence,
            "answer": get_answer(sentence, context=chat)
        }

        chat.append(turn)
        session["chat"] = chat
    
        answer = turn["answer"]

    return _html_answer(answer)


def _html_answer(answer):

    html_text = answer
    if type(html_text) == dict:
        html_text = f"<p>{answer['text']}<br>"
        results = answer["results"]

        max_rows = len(results)
        for index, row in enumerate(results):
            html_text += f'<br><b><i class="fas fa-hashtag"></i> {index+1}</b><br>'
            for key, value in row.items():
                html_text += f"<b>{key}:</b> {value}<br>"
        html_text += "</p>"

    return f"""
    <div class="bot-content">
    {html_text}
    </div> 
    """


def process_start_session():
    """Inicia uma nova sessão de usuário.

    Returns:
        dict: Resposta da sessão criada
    """
    if "user_id" in session:
        del session['user_id']
        del session['chat']
    user_id = uuid.uuid4()
    session['user_id'] = user_id
    session['chat'] = list()

    response = jsonify(
        status="success",
        message="Session updated successfully!"
    )
    response.status_code = HTTPStatus.CREATED
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response