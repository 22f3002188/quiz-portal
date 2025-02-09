from flask import Flask, render_template, request, redirect, url_for, flash, session
from backend.models import db, User, create_admin, Subject, Chapter, Quiz
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            if user.role == 'admin':
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        #username = request.form.get('email')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() 

        new_user = User(
            #username=username,
            email=email,
            password=password,
            full_name=full_name,
            qualification=qualification,
            dob=dob
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/user_dashboard')
def user_dashboard():
    return render_template('user.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/chapter', methods=['GET', 'POST'])
def add_chapter():
    if request.method == 'POST':
        chapter_name = request.form['name']
        chapter_description = request.form['description']
        new_chapter = Chapter(name=chapter_name, description=chapter_description, subject_id=1)  # Replace subject_id with the appropriate value
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('chapter.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    all_subjects = Subject.query.all()  # Fetch only subjects, no chapters
    return render_template('admin.html', subjects=all_subjects)

@app.route('/subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        subject_name = request.form['name']
        subject_description = request.form['description']
        new_subject = Subject(name=subject_name, description=subject_description)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('subject.html')

@app.route('/subjects', methods=['GET'])
def subjects():
    all_subjects = Subject.query.all()  # Only fetching subjects
    return render_template('subjects.html', subjects=all_subjects)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database tables are created
        create_admin(app)  # Create the admin user

        # Retrieve subjects once and store them in a global variable
        # all_subjects = Subject.query.all()

        # Print retrieved subjects for debugging
        # for subject in all_subjects:
        #     print(subject.id, subject.name, subject.description)  
    app.run(debug=True)