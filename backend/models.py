from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    #username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    role = db.Column(db.String(10), default='user') # 'admin' or 'user'

    def __init__(self, email, password, role):
        self.email = email
        self.password = password
        self.role = role


def create_admin(app):
    with app.app_context():
        if not User.query.filter_by(email='admin@gmail.com').first():
            admin = User(
                #username='admin@gmail.com',  # Set the username field
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




# class Subject(db.Model):
#     __tablename__ = 'subjects'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)

# class Chapter(db.Model):
#     __tablename__ = 'chapters'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
# class Subject(db.Model):
#     __tablename__ = 'subjects'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)

# class Chapter(db.Model):
#     __tablename__ = 'chapters'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

# class Quiz(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
#     date_of_quiz = db.Column(db.Date)
#     time_duration = db.Column(db.String(10))
#     remarks = db.Column(db.Text)

# class Question(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
#     question_statement = db.Column(db.Text)
#     option1 = db.Column(db.String(100))
#     option2 = db.Column(db.String(100))
#     option3 = db.Column(db.String(100))
#     option4 = db.Column(db.String(100))
#     correct_option = db.Column(db.String(100))

# class Score(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     time_stamp_of_attempt = db.Column(db.DateTime)
#     total_scored = db.Column(db.Integer)


