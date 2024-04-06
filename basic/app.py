from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

#Constants for consistency 
RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

@app.route("/")
def show_survey_start():
    """Selecting a survey"""

    return render_template("survey_start.html", survey=survey)

@app.route("/begin", methods=["POST"])
def start_survey():
    """Clearing session of responses"""

    session[RESPONSES_KEY] = []
    
    return redirect("/questions/0")

@app.route("/answer", methods=["POST"])
def handle_question():
    """Saving response and then redirect to next question"""

    #response choice
    choice = request.form['answer']

    #add response to session
    responses = session[RESPONSES_KEY]
    responses.append(choice)
    session[RESPONSES_KEY] = responses

    if(len(responses) == len(survey.questions)):
        #they have responded to all the survey questions
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")

@app.route("questions/<int:qid>")
def show_question(qid):
    """Display current question ID"""
    responses = session.get(RESPONSES_KEY)

    if(responses is None):
        #if user tries to access question page without answering
        return redirect("/")

    if(len(responses) == len(survey.questions)):
        #they have responded to all the survey questions
        return redirect("/complete")

    if(len(responses) != qid):
        #when a user tries to access questions out of order
        flash(f"WRONG question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]
    return render_template("questions.html", question_num=qid, question=question)

@app.route("/complete")
def complete():
    """User completed survey, now show completion page"""

    return render_template("completion.html")


    
