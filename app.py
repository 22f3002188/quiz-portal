from flask import Flask, render_template, request, redirect, url_for, flash, session
from backend.models import Score, create_admin, db, User, Subject, Chapter, Quiz, Question
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_portal.db' #having db file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)  # flask app is connected to db(connecting sqlalchemy)

        #  ---------login--------
@app.route('/')
def home():
        return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:   
            flash('Please fill all the fields')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()  # Check if user exists

        if not user:
            flash('User does not exist!')
            return redirect(url_for('login'))

        # Use check_password_hash to compare hashed passwords
        if user and user.password == password:
            session['user_id'] = user.id  # Store user ID in session after successful login
            session['full_name'] = user.full_name  # Store username in session
            
            if user.role == 'admin':
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('all_quizzes'))  
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

#  Displaying a webpage (e.g., showing a form, displaying data)
#  render_template: Used to display a web page (e.g., showing a form, displaying data).

 
                        #  --------signup--------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() 

        if not email or not password or not full_name or not qualification or not dob:
            flash('Please fill all the fields')
            return redirect(url_for('signup'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('User already exists!')
            return redirect(url_for('signup'))    

        new_user = User(         #database object is created
            email=email,
            password=password,
            full_name=full_name,
            qualification=qualification,
            dob=dob
        )
        db.session.add(new_user)      # push to database
        db.session.commit()           # commit to database (permanent save)
        flash('Signup successful!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')    


        # <-----admin_dashboard----->
@app.route('/admin')
def admin_dashboard():
    subjects = Subject.query.all()
    return render_template('admin.html', subjects=subjects)
  

# -----------------------subjects-----------------------

@app.route('/subject/add', methods=['GET', 'POST'])
def manage_subjects():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if not name or not description:
            flash('Please fill all the fields')
            return redirect(url_for('manage_subjects'))
        
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!')
        return redirect(url_for('admin_dashboard'))
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/subject/edit/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):
    subject = Subject.query.get(id)
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_subject.html', subject=subject)

@app.route('/subject/delete/<int:id>', methods=['POST'])
def delete_subject(id):
    subject = Subject.query.get(id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

#----------------------chapters----------------------

@app.route('/subject/<int:subject_id>/chapters')
def view_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('view_chapters.html', subject=subject, chapters=chapters)

@app.route('/subject/<int:subject_id>/chapter/add', methods=['GET', 'POST'])
def add_chapter(subject_id):
    subject = Subject.query.get(subject_id)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if not name or not description:
            flash('Please fill all the fields', 'danger')
            return redirect(url_for('chapter.html', subject_id=subject_id))

        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('view_chapters', subject_id=subject_id))
    return render_template('chapter.html', subject=subject)

@app.route('/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('view_chapters', subject_id=chapter.subject_id))
    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/chapter/<int:chapter_id>/delete', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('view_chapters', subject_id=chapter.subject_id))

#----------------------quizzes----------------------

@app.route('/chapter/<int:chapter_id>/quizzes')
def view_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('view_quizzes.html', chapter=chapter, quizzes=quizzes)

@app.route('/chapter/<int:chapter_id>/quiz/add', methods=['GET', 'POST'])
def add_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        quiz_name = request.form.get('quiz_name')  # Get quiz name from form
        date_str = request.form.get('date_of_quiz')
        time_str = request.form.get('time_duration')

        if not quiz_name:  # Ensure quiz name is provided
            flash('Quiz name is required!', 'danger')
            return redirect(request.referrer)

        date_of_quiz = datetime.strptime(date_str, "%Y-%m-%d").date()  # Convert to `date` object
        time_duration = datetime.strptime(time_str, "%H:%M").time()  # Convert to `time` object

        new_quiz = Quiz(
            quiz_name=quiz_name,  # Include quiz name
            chapter_id=chapter_id, 
            date_of_quiz=date_of_quiz, 
            time_duration=time_duration
        )
        db.session.add(new_quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('view_quizzes', chapter_id=chapter_id))

    return render_template('add_quiz.html', chapter=chapter)


@app.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        quiz_name = request.form.get('quiz_name')  # Get quiz name
        date_str = request.form.get('date_of_quiz')
        time_str = request.form.get('time_duration')

        if not quiz_name:  # Ensure quiz name is provided
            flash('Quiz name is required!', 'danger')
            return redirect(request.referrer)

        quiz.quiz_name = quiz_name  # Update quiz name
        quiz.date_of_quiz = datetime.strptime(date_str, "%Y-%m-%d").date()  # Convert to `date`
        quiz.time_duration = datetime.strptime(time_str, "%H:%M").time()  # Convert to `time`
    
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('view_quizzes', chapter_id=quiz.chapter_id))

    return render_template('edit_quiz.html', quiz=quiz)


@app.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('view_quizzes', chapter_id=quiz.chapter_id))

#----------------------questions----------------------

@app.route('/quiz/<int:quiz_id>/questions')
def view_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch the quiz object
    questions = Question.query.filter_by(quiz_id=quiz_id).all()  # Fetch questions related to this quiz
    return render_template('view_questions.html', quiz=quiz, questions=questions)  # Pass 'quiz' to the template

@app.route('/quiz/<int:quiz_id>/question/add', methods=['GET', 'POST'])
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch quiz details to pass into the template

    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = request.form['correct_answer']

        # Validate all options are provided
        if not (option1 and option2 and option3 and option4):
            flash("All four options are required.", "danger")
            return redirect(url_for('add_question', quiz_id=quiz_id))

        # Validate correct answer is one of the provided options
        if correct_answer not in ["option1", "option2", "option3", "option4"]:
            flash("Correct answer must be one of the provided options.", "danger")
            return redirect(url_for('add_question', quiz_id=quiz_id))

        # Create new question entry
        new_question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_answer=correct_answer
        )
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for('view_questions', quiz_id=quiz_id))

    return render_template('add_question.html', quiz=quiz)

@app.route('/quiz/<int:quiz_id>/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch quiz details
    question = Question.query.get_or_404(question_id)  # Fetch question details

    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = request.form['correct_answer']

        # Validate all options are provided
        if not (option1 and option2 and option3 and option4):
            flash("All four options are required.", "danger")
            return redirect(url_for('edit_question', quiz_id=quiz_id, question_id=question_id))

        # Validate correct answer is one of the provided options
        if correct_answer not in ["option1", "option2", "option3", "option4"]:
            flash("Correct answer must be one of the provided options.", "danger")
            return redirect(url_for('edit_question', quiz_id=quiz_id, question_id=question_id))

        # Update question details
        question.question_statement = question_statement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_answer = correct_answer

        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for('view_questions', quiz_id=quiz_id))

    return render_template('edit_question.html', quiz=quiz, question=question)

@app.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for('view_questions', quiz_id=question.quiz_id))

#--------------------------------users list--------------------------------

@app.route('/users')
def users():
    users = User.query.filter(User.email != 'admin@gmail.com').all()  # Exclude admin
    return render_template('users_list.html', users=users)

@app.route('/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)  # Fetch user by ID
    db.session.delete(user)  # Delete the user from the database
    db.session.commit()  # Commit the deletion
    
    return redirect(url_for('users')) 

#----------------------search--------------------------------
@app.route('/search')
def search():
    query = request.args.get('q', '').strip()

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('admin_dashboard'))

    # Perform case-insensitive search using SQLAlchemy `ilike`
    users = User.query.filter(User.email.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f"%{query}%")).all()

    return render_template('search_results.html', query=query, users=users, subjects=subjects, chapters=chapters, quizzes=quizzes)




# ----------------------user_dashboard--------------------------------


@app.route('/quizzes', methods=['GET'])
def all_quizzes():
    current_date = date.today()  # Get today's date

    quizzes_query = (
        db.session.query(
            Quiz.id, 
            Quiz.quiz_name, 
            Quiz.time_duration, 
            Quiz.date_of_quiz, 
            Chapter.name.label("chapter"), 
            Subject.name.label("subject")
        )
        .join(Chapter, Quiz.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
    )


    quizzes = quizzes_query.all()

    # Convert all `date_of_quiz` to `date` objects safely
    formatted_quizzes = []
    for quiz in quizzes:
        formatted_quizzes.append({
            "id": quiz.id,
            "quiz_name": quiz.quiz_name,
            "time_duration": quiz.time_duration,
            "date_of_quiz": quiz.date_of_quiz.date() if isinstance(quiz.date_of_quiz, datetime) else quiz.date_of_quiz,
            "chapter": quiz.chapter,
            "subject": quiz.subject
        })

    return render_template('users.html', quizzes=formatted_quizzes, current_date=current_date)



@app.route('/quiz/<int:quiz_id>/attempt', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = quiz.chapter  # Get the chapter associated with this quiz
    subject = chapter.subject  # Get the subject associated with the chapter
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if request.method == 'POST':
        user_score = 0
        
        # Check answers for each question
        for question in questions:
            user_answer = request.form.get(f'q{question.id}')
            
            # Compare user's answer to the correct answer (by matching with the selected option)
            if user_answer == getattr(question, question.correct_answer):
                user_score += 1
        
        # Save the score in the database
        user_id = session.get('user_id')  # Assuming the user ID is stored in the session
        
        score_entry = Score(
            user_id=user_id,  # Get user_id from session or pass it from the frontend
            quiz_id=quiz_id,
            score=user_score,  # Total score
        )
        db.session.add(score_entry)
        db.session.commit()

        # Render the score directly (as a number)
        return render_template('show_score.html', score=user_score, total=len(questions))
    
    return render_template('attempt_quiz.html', quiz=quiz, questions=questions)



@app.route('/score/<int:score_id>', methods=['GET'])
def show_score(score_id):
    score_entry = Score.query.get_or_404(score_id)
    return render_template('show_score.html', score_entry=score_entry)



@app.route('/user/scores', methods=['GET'])
def user_scores():
    user_id = session.get('user_id')  # Get the logged-in user's ID from session
    
    # Query to get the scores for the logged-in user
    scores_query = db.session.query(
        Score.score,
        Quiz.quiz_name,
        Chapter.name.label('chapter'),
        Subject.name.label('subject')
    ).join(Quiz, Score.quiz_id == Quiz.id) \
     .join(Chapter, Quiz.chapter_id == Chapter.id) \
     .join(Subject, Chapter.subject_id == Subject.id) \
     .filter(Score.user_id == user_id)  # Only get scores for the current user

    scores = scores_query.all()  # Execute the query
    
    return render_template('user_scores.html', scores=scores)

from flask import request, flash, redirect, url_for, render_template

@app.route('/search_quizzes')
def search_quizzes():
    query = request.args.get('q', '').strip()

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('all_quizzes'))  # Redirect to all quizzes if no query is provided

    # Perform case-insensitive search using SQLAlchemy `ilike`
    quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()

    return render_template('search_quizzes.html', query=query, quizzes=quizzes, subjects=subjects)






# ----------------------logout--------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():  # is used to push the application context for performing operations that require access to the current Flask app.
        db.create_all()   # create all tables in the database if they don't exist already
    create_admin(app)
    app.run(debug=True)