from flask import Flask, render_template, redirect, url_for, flash, request
from extensions import db, login_manager
from models import User, Post, SocialAccount
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import os

from werkzeug.utils import secure_filename
from flask_apscheduler import APScheduler
from utils import generate_verification_token, confirm_verification_token
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key_change_this_later' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SCHEDULER_API_ENABLED'] = True

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_verified:
        flash('Please verify your email address to access the dashboard.', 'warning')
        return render_template('unverified.html') # New template needed

    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    accounts = SocialAccount.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, posts=posts, accounts=accounts)

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content')
    file = request.files.get('file')
    schedule_option = request.form.get('schedule_option') # 'now' or 'later'
    scheduled_time_str = request.form.get('scheduled_time')
    
    image_path = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = f'uploads/{filename}'
    
    final_status = 'scheduled'
    final_time = None
    
    if schedule_option == 'now':
        final_status = 'published' # In a real app, we'd trigger the publish job immediately
        final_time = datetime.utcnow()
        flash('Post published immediately! (Mock)', 'success')
    elif scheduled_time_str:
        try:
            final_time = datetime.strptime(scheduled_time_str, '%Y-%m-%dT%H:%M')
            flash(f'Post scheduled for {scheduled_time_str}', 'success')
        except ValueError:
            final_time = datetime.utcnow()
            flash('Invalid date format, scheduled for now.', 'warning')

    new_post = Post(user_id=current_user.id, content=content, image_path=image_path, status=final_status, scheduled_time=final_time)
    db.session.add(new_post)
    db.session.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/connect_account/<platform>', methods=['GET', 'POST'])
@login_required
def connect_account(platform):
    if request.method == 'POST':
        handle = request.form.get('handle')
        existing = SocialAccount.query.filter_by(user_id=current_user.id, platform=platform).first()
        if not existing:
            new_account = SocialAccount(user_id=current_user.id, platform=platform, username=f"@{handle}")
            db.session.add(new_account)
            db.session.commit()
            flash(f'Connected to {platform.capitalize()} as @{handle}!', 'success')
        else:
             flash(f'Already connected to {platform.capitalize()}', 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('connect.html', platform=platform)

@app.route('/cancel_post/<int:post_id>')
@login_required
def cancel_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('dashboard'))
        
    if post.status == 'scheduled':
        db.session.delete(post)
        db.session.commit()
        flash('Scheduled post cancelled.', 'success')
    else:
        flash('Cannot cancel a post that is already published or draft.', 'warning')
        
    return redirect(url_for('dashboard'))

@app.route('/verify/<token>')
def verify_email(token):
    email = confirm_verification_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('login'))
        
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash('Account already verified. Please login.', 'success')
    else:
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                flash('Please check your console/email to verify your account first.', 'warning')
                # For demo purposes, we might still allow login or block. 
                # Strict: block.
                # return render_template('auth.html', mode='login')
                # Loose (for easy testing): allow but restrict dashboard (implemented in dashboard route).
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('auth.html', mode='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password) 
        new_user = User(username=username, email=email, password_hash=hashed_pw, is_verified=False)
        db.session.add(new_user)
        db.session.commit()
        
        token = generate_verification_token(new_user.email)
        verify_url = url_for('verify_email', token=token, _external=True)
        print(f"\n==========================================")
        print(f"SIMULATED EMAIL TO: {email}")
        print(f"VERIFY LINK: {verify_url}")
        print(f"==========================================\n")
        
        flash('A verification link has been sent to your email (Check Console).', 'info')
        return redirect(url_for('login'))
    return render_template('auth.html', mode='register')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Background Job
@scheduler.task('interval', id='publish_posts', seconds=60)
def publish_posts_job():
    with app.app_context():
        now = datetime.utcnow()
        # Find posts that are scheduled and due
        posts_due = Post.query.filter(Post.status == 'scheduled', Post.scheduled_time <= now).all()
        for post in posts_due:
            post.status = 'published'
            # Here we would call the actual API for the connected social account
            print(f"Background Job: Published post {post.id} for user {post.user_id}")
            db.session.add(post)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
             os.makedirs(app.config['UPLOAD_FOLDER'])
        db.create_all()
    app.run(debug=True, port=8000)