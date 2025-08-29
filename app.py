from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Ticket, Notification
from utils import send_email, generate_csv, generate_pdf
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketing.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'head':
                return redirect(url_for('head_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Head Dashboard
@app.route('/head_dashboard')
@login_required
def head_dashboard():
    if current_user.role != 'head':
        return "Access Denied"
    tickets = Ticket.query.all()
    notifications = Notification.query.filter_by(target_role='head').all()
    return render_template('head_dashboard.html', tickets=tickets, notifications=notifications)

# Admin Dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Access Denied"
    tickets = Ticket.query.filter_by(assigned_to=current_user.id).all()
    notifications = Notification.query.filter_by(target_role='admin').all()
    return render_template('admin_dashboard.html', tickets=tickets, notifications=notifications)

# User Dashboard
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return "Access Denied"
    tickets = Ticket.query.filter_by(created_by=current_user.id).all()
    notifications = Notification.query.filter_by(target_role='user').all()
    return render_template('user_dashboard.html', tickets=tickets, notifications=notifications)

# Submit Ticket
@app.route('/submit_ticket', methods=['GET', 'POST'])
@login_required
def submit_ticket():
    if current_user.role != 'user':
        return "Access Denied"
    if request.method == 'POST':
        issue_type = request.form['issue_type']
        description = request.form['description']
        file = request.files['attachment']
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ticket = Ticket(issue_type=issue_type, description=description, attachment=filename, created_by=current_user.id)
        db.session.add(ticket)
        db.session.commit()
        flash("Ticket Submitted Successfully")
        return redirect(url_for('user_dashboard'))
    return render_template('submit_ticket.html')

# Notifications
@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    if current_user.role != 'head':
        return "Access Denied"
    if request.method == 'POST':
        content = request.form['content']
        target_role = request.form['target_role']
        notif = Notification(content=content, created_by=current_user.id, target_role=target_role)
        db.session.add(notif)
        db.session.commit()
        flash("Notification Sent")
    return render_template('notifications.html')

# Export Reports
@app.route('/export_csv')
@login_required
def export_csv():
    if current_user.role == 'head':
        tickets = Ticket.query.all()
    elif current_user.role == 'admin':
        tickets = Ticket.query.filter_by(assigned_to=current_user.id).all()
    else:
        tickets = Ticket.query.filter_by(created_by=current_user.id).all()
    output = generate_csv(tickets)
    return send_file(output, download_name="tickets.csv", as_attachment=True)

@app.route('/export_pdf')
@login_required
def export_pdf():
    if current_user.role == 'head':
        tickets = Ticket.query.all()
    elif current_user.role == 'admin':
        tickets = Ticket.query.filter_by(assigned_to=current_user.id).all()
    else:
        tickets = Ticket.query.filter_by(created_by=current_user.id).all()
    output = generate_pdf(tickets)
    return send_file(output, download_name="tickets.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
