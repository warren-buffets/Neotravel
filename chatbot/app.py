from flask import Flask, render_template, request, session, redirect
from chatbot_logic import questions_flow
from utils import generate_summary, save_request_to_json
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key")

# 🟢 ROUTE PRINCIPALE (CHATBOT)
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'step' not in session:
        session['step'] = 0
        session['responses'] = {}

    if request.method == 'POST':
        user_input = request.form['message']
        current_question = questions_flow[session['step']]
        session['responses'][current_question['key']] = user_input
        session['step'] += 1

    if session['step'] < len(questions_flow):
        next_question = questions_flow[session['step']]['question']
        summary = None
    else:
        next_question = None
        summary = generate_summary(session['responses'])
        save_request_to_json(session['responses'])
        session.clear()

    return render_template(
        'index.html',
        question=next_question,
        summary=summary,
        responses=session.get('responses', {}),
        questions=questions_flow
    )

# 🔵 ROUTE ADMIN POUR HISTORIQUE DES DEMANDES
@app.route('/admin')
def admin():
    try:
        with open("data/requests.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    return render_template('admin.html', requests=data)

# 🔁 ROUTE POUR MODIFIER UNE RÉPONSE
@app.route('/edit/<key>', methods=['POST'])
def edit_response(key):
    if 'responses' in session and key in session['responses']:
        del session['responses'][key]
        step = next(i for i, q in enumerate(questions_flow) if q['key'] == key)
        session['step'] = step
    return redirect('/')

# 🚀 Lancement
if __name__ == '__main__':
    app.run(debug=True)
