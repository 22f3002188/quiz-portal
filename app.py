from flask import Flask, render_template, request, redirect, url_for, flash, session
from backend.models import create_admin, db, User, Subject, Chapter, Quiz, Question
from datetime import datetime

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

        user = User.query.filter_by(email=email).first()  # available in database or not checking

        if not user:
            flash('User does not exist!')
            return redirect(url_for('login'))

        if user and user.password == password:
            if user.role == 'admin':
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('user_dashboard'))  
            #Navigation after an action (e.g., login, form submission)
             #redirect: Used after performing an action that requires the user to be taken to a different page (e.g., after form submission, login, logout).
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')
 #Displaying a webpage (e.g., showing a form, displaying data)
 #render_template: Used to display a web page (e.g., showing a form, displaying data).
 
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
    chapters = Chapter.query.all()  # Fetch all chapters
    return render_template('admin.html', subjects=subjects, chapters=chapters)
  


# CRUD for Subjects
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

@app.route('/chapter/<int:chapter_id>/quizzes')
def view_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('view_quizzes.html', chapter=chapter, quizzes=quizzes)

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

@app.route('/chapter/<int:chapter_id>/quiz/add', methods=['GET', 'POST'])
def add_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        date_of_quiz = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        question_statements = request.form.getlist('question_statement[]')
        option1_list = request.form.getlist('option1[]')
        option2_list = request.form.getlist('option2[]')
        option3_list = request.form.getlist('option3[]')
        option4_list = request.form.getlist('option4[]')
        correct_answers = request.form.getlist('correct_answer[]')

        if not date_of_quiz or not time_duration or not question_statements:
            flash('Please fill all fields.', 'danger')
            return redirect(url_for('add_quiz', chapter_id=chapter_id))

        try:
            date_parsed = datetime.strptime(date_of_quiz, '%Y-%m-%d %H:%M')
            time_parsed = datetime.strptime(time_duration, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return redirect(url_for('add_quiz', chapter_id=chapter_id))

        new_quiz = Quiz(
            chapter_id=chapter_id,
            date_of_quiz=date_parsed,
            time_duration=time_parsed
        )
        db.session.add(new_quiz)
        db.session.commit()

        for i in range(len(question_statements)):
            new_question = Question(
                quiz_id=new_quiz.id,
                statement=question_statements[i],
                option1=option1_list[i],
                option2=option2_list[i],
                option3=option3_list[i] if option3_list[i] else None,
                option4=option4_list[i] if option4_list[i] else None,
                correct_answer=correct_answers[i]
            )
            db.session.add(new_question)

        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('view_quizzes', chapter_id=chapter_id))

    return render_template('add_quiz.html', chapter=chapter)



# @app.route('/quiz/edit/<int:id>', methods=['GET', 'POST'])
# def edit_quiz(id):
#     """Handles editing a quiz's date and duration."""
#     quiz = Quiz.query.get_or_404(id)

#     if request.method == 'POST':
#         date_of_quiz = request.form['date_of_quiz']
#         time_duration = request.form['time_duration']

#         if not date_of_quiz or not time_duration:
#             flash('Please fill all fields.', 'danger')
#             return redirect(url_for('edit_quiz', id=id))

#         try:
#             quiz.date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d %H:%M')
#             quiz.time_duration = datetime.strptime(time_duration, '%H:%M').time()
#         except ValueError:
#             flash('Invalid date or time format.', 'danger')
#             return redirect(url_for('edit_quiz', id=id))

#         db.session.commit()
#         flash('Quiz updated successfully!', 'success')
#         return redirect(url_for('view_quizzes', chapter_id=quiz.chapter_id))

#     return render_template('edit_quiz.html', quiz=quiz)


@app.route('/quiz/delete/<int:id>', methods=['POST'])
def delete_quiz(id):
    """Handles deleting a quiz."""
    quiz = Quiz.query.get_or_404(id)
    chapter_id = quiz.chapter_id

    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')

    return redirect(url_for('view_quizzes', chapter_id=chapter_id))





# <-----user_dashboard----->


@app.route('/user_dashboard')
def user_dashboard():
    return render_template('user.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# @app.route('/quiz')
# def quiz():
#     return render_template('quiz.html')

# @app.route('/result')   
# def result():
#     return render_template('score.html')

if __name__ == '__main__':
    with app.app_context():  # is used to push the application context for performing operations that require access to the current Flask app.
        db.create_all()   # create all tables in the database if they don't exist already
    create_admin(app)
    app.run(debug=True)