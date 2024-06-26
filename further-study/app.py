from flask import Flask, session, request, render_template, redirect, make_response, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

#Constants for consistency 
CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

@app.route("/")
def show_pick_survey_start():
    """Pick-a-survey form"""

    return render_template("pick-survey.html", surveys=surveys)

@app.route("/", methods=["POST"])
def pick_survey():
    """Select survey"""

    survey_id = request.form['survey_code']

    #stops user from retaking a survey until cookie times out
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-done.html")

    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

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
    text = request.form.get("text", "")

    #add response to the list in the session
    responses = session[RESPONSES_KEY]
    responses.append({"choice": choice, "text": text})

    #add response to session
    session[RESPONSES_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if(len(responses) == len(survey.questions)):
        #they have responded to all the survey questions
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")

@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question ID"""

    responses = session.get(RESPONSES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

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
def say_thanks():
    """User completed survey, thank user and list responses"""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html = render_template("completion.html", survey=survey, responses=responses)

    #set cookie as survey being complete and letting user know they cant redo
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)

    return response



    
