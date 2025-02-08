from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

users = {
    'admin': {'password': 'admin', 'role': 'instructor'},
    'user': {'password': 'user', 'role': 'student'}
}

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('instructor', 'Instructor')], validators=[DataRequired()])
    submit = SubmitField('Login')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    user_role = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    comments = db.relationship('Comment', backref='message', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(150), nullable=False)
    user_role = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)

# Ensure database tables are created before the first request
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data
        
        if username in users and users[username]['password'] == password and users[username]['role'] == role:
            session['user'] = username
            session['role'] = users[username]['role']
            flash('Login successful!', 'success')
            return redirect(url_for('message_board'))
        else:
            flash('Invalid username/password/role', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/message_board', methods=['GET', 'POST'])
def message_board():
    if 'user' not in session:
        flash('Please log in first', 'warning')
        return redirect(url_for('login'))
    
    form = MessageForm()
    if form.validate_on_submit():
        new_message = Message(username=session['user'], user_role=session['role'], content=form.message.data)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('message_board'))
    
    messages = Message.query.all()
    return render_template('message_board.html', username=session['user'], form=form, messages=messages)

@app.route('/message/<int:message_id>', methods=['GET', 'POST'])
def view_message(message_id):
    if 'user' not in session:
        flash('Please log in first', 'warning')
        return redirect(url_for('login'))
    message = Message.query.get_or_404(message_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        new_comment = Comment(user=session['user'], user_role=session['role'], content=comment_form.comment.data, message_id=message.id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('view_message', message_id=message.id))

    return render_template('view_message.html', message=message, comment_form=comment_form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
