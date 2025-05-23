from flask import Flask, render_template, request, session, redirect, make_response
from chatbot_logic import get_dynamic_questions, generate_predevis
from utils import generate_summary, save_request_to_json
from xhtml2pdf import pisa
from flask_mail import Mail, Message
from io import BytesIO
from datetime import datetime
import os
import json
from dotenv import load_dotenv

# Load .env config
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key")

# Flask-Mail config
app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS") == "True",
    MAIL_USE_SSL=os.getenv("MAIL_USE_SSL") == "True",
)
mail = Mail(app)

def send_predevis_email(recipient_email, rendered_html):
    pdf_bytes = BytesIO()
    pisa.pisaDocument(BytesIO(rendered_html.encode("utf-8")), dest=pdf_bytes)

    msg = Message(
        subject="Votre pré-devis Neotravel ✨",
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[recipient_email]
    )
    msg.body = (
        "Bonjour,\n\n"
        "Veuillez trouver ci-joint votre pré-devis Neotravel.\n"
        "Pour valider votre demande, répondez à ce message en indiquant la référence indiquée dans le document.\n\n"
        "L'équipe Neotravel"
    )
    msg.attach("predevis.pdf", "application/pdf", pdf_bytes.getvalue())
    mail.send(msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'step' not in session:
        session['step'] = 0
        session['responses'] = {}

    if request.method == 'POST':
        user_input = request.form['message']
        questions_flow = get_dynamic_questions(session['responses'])

        if session['step'] < len(questions_flow):
            current_question = questions_flow[session['step']]
            session['responses'][current_question['key']] = user_input
            session['step'] += 1

    questions_flow = get_dynamic_questions(session['responses'])

    if session['step'] < len(questions_flow):
        next_question = questions_flow[session['step']]['question']
        summary = None
    else:
        next_question = None
        summary = generate_summary(session['responses'])
        save_request_to_json(session['responses'])
        session['devis'] = generate_predevis(session['responses'])

    return render_template(
        'index.html',
        question=next_question,
        summary=summary,
        responses=session.get('responses', {}),
        questions=questions_flow
    )

@app.route('/edit/<key>', methods=['POST'])
def edit_response(key):
    if 'responses' in session and key in session['responses']:
        del session['responses'][key]
        questions_flow = get_dynamic_questions(session['responses'])
        for i, q in enumerate(questions_flow):
            if q["key"] == key:
                session["step"] = i
                break
    return redirect('/')

@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return redirect('/')

@app.route('/admin')
def admin():
    try:
        with open("data/requests.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    return render_template('admin.html', requests=data)

@app.route('/devis')
def show_devis():
    if 'devis' not in session:
        return redirect('/')
    return render_template('devis.html', devis=session['devis'])

@app.route('/devis/pdf')
def download_pdf():
    if 'responses' not in session or 'devis' not in session:
        return redirect('/')

    rendered_html = render_template(
        'devis_pdf.html',
        devis=session['devis'],
        today=datetime.today().strftime("%d/%m/%Y")
    )

    recipient = session['responses'].get('email')
    if recipient:
        try:
            send_predevis_email(recipient, rendered_html)
        except Exception as e:
            print("Erreur envoi mail :", e)

    pdf_result = BytesIO()
    pisa.pisaDocument(BytesIO(rendered_html.encode("utf-8")), dest=pdf_result)

    response = make_response(pdf_result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=predevis.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
