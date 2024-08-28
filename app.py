from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
import bcrypt
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

#index page hosting-----

@app.route('/')
def index():
    return render_template('home.html')

# register_page hosting----

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method== 'POST':
        # handle request
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        new_user= User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')


    return render_template('register.html')

# login_page hosting----

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method== 'POST':
        # handle request
        email=request.form['email']
        password=request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['name']= user.name
            session['email']= user.email
            session['password']= user.password
            return redirect('/games')
        else:
            return render_template('login.html',error='invalid user')

    return render_template('login.html')
    


# games_page hosting start -------------------------

@app.route('/games', methods=['GET','POST'])
def games():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('games.html',user=user)
    else:
        return redirect('/login')

# ------------------------------------------
# number_gussing_game: 

@app.route('/num_game', methods=['GET', 'POST'])
def num_game():
    if request.method == 'POST':
        top_of_range = request.form['top_of_range']
        if top_of_range.isdigit() and int(top_of_range) > 0:
            session['top_of_range'] = int(top_of_range)
            session['random_no'] = random.randint(0, int(top_of_range))
            session['count'] = 0
            return redirect(url_for('num_guess'))
        else:
            return render_template('num_game.html', message='Please enter a valid number greater than 0.')

    # Clear previous session/game data
    session.clear()
    return render_template('num_game.html', message=None)

@app.route('/num_guess', methods=['GET', 'POST'])
def num_guess():
    if 'random_no' not in session:
        return redirect(url_for('num_game'))

    if request.method == 'POST':
        user_guess = request.form['user_guess']
        if user_guess.isdigit():
            user_guess = int(user_guess)
            session['count'] += 1
            if user_guess == session['random_no']:
                congratulations_message = f'You got it user! you got it in {session["count"]} tries.'
                session.clear()  # Reset/clear the session after the game is over
                return render_template('gameover_num.html', message=congratulations_message)
            elif user_guess > session['random_no']:
                message = 'You are above the number!'
            else:
                message = 'You are below the number!'
            return render_template('num_guess.html', message=message)
        else:
            return render_template('num_guess.html', message='Please enter a valid number!')

    return render_template('num_guess.html', message=None)

# -------------------------------------------------------------------------
# rock_paper_sessores_game: 

@app.route("/rock_paper_sessores_game", methods=["GET", "POST"])
def rock_paper_sessores_game():
    a=0
    if request.method == "POST":
        user_input = request.form['choice'].lower()
        if user_input == 'q':
            return redirect(url_for('game_over_rock'))
        
        options = ['rock', 'paper', 'scissors']
        system_pick = random.choice(options)
        outcome = ""
        if user_input not in options:
            outcome = "Invalid option, try again."
        else:
            if (user_input == "rock" and system_pick == "scissors") or \
               (user_input == "paper" and system_pick == "rock") or \
               (user_input == "scissors" and system_pick == "paper"):
                outcome = "You won!"
                a+=1
            else:
                outcome = "You lost!"
        
        return render_template("rock_paper_game.html", outcome=outcome, system_pick=system_pick, user_input=user_input)
    else:
        return render_template("rock_paper_game.html", outcome=None)


#---------------------------------------------------------------------------
# quiz_game:
 
@app.route('/quiz_game', methods=['GET', 'POST'])
def quiz_game():
    if request.method == 'POST':
        score = 0
        questions = [
            ("what does CPU stand for? ", "central processing unit"),
            ("what does GPU stand for? ", "graphical processing unit"),
            ("what does BST stand for? ", "binary search tree"),
            ("what does BT stand for? ", "binary tree")
        ]
        
        for question, answer in questions:
            user_input = request.form.get(question.strip())
            if user_input and user_input.lower() == answer:
                score += 1
        
        return render_template("quiz_result.html", score=score, total=len(questions))
    
    return render_template("quiz_game.html")
# games_page hosting end ------------------------------    

@app.route('/game_over_num')
def game_over_num():
    return render_template('games.html')
#-----------------------------------------------------

@app.route('/game_over_rock')
def game_over_rock():
    return render_template('gameover_rock.html')



#logout page---
@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')


if __name__=="__main__":
    app.run(debug=True)