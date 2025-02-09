
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    role = db.Column(db.String(10), default='user')
    scores = db.relationship('Score', backref='user', cascade='all, delete-orphan') # 'admin' or 'user

    # def __init__(self, email, password, role):
    #     self.email = email
    #     self.password = password
    #     self.role = role


def create_admin(app):
    with app.app_context():
        if not User.query.filter_by(email='admin@gmail.com').first():
            admin = User(
                email='admin@gmail.com',
                password='123456',
                full_name='ADMIN',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")
        else:
            print("Admin user already exists.")

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', cascade='all, delete-orphan')

    
class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    # Relationship to quizzes (one-to-many)
    quizzes = db.relationship('Quiz', backref='chapter', cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    remarks = db.Column(db.String)
    # Relationship to questions (one-to-many)
    questions = db.relationship('Question', backref='quiz', cascade='all, delete-orphan')
    # Relationship to track scores for this quiz
    scores = db.relationship('Score', backref='quiz', cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    question_statement = db.Column(db.String, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String)
    option4 = db.Column(db.String)
    correct_answer = db.Column(db.String, nullable=False)

class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Float, nullable=False)  # Percentage or total score