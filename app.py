from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, flash, send_from_directory
import sqlite3
import datetime
import os
import bcrypt
from functools import wraps

app = Flask(__name__)
app.config['DATABASE'] = 'debate.sqlite'
app.secret_key = 'your_secret_key'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def is_logged_in():
    return 'username' in session


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def login_required_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


# Display homepage
@app.route('/')
def home():
    logged_in = is_logged_in()
    db = get_db()
    cursor = db.cursor()
    
    # Get all topics with their metadata and like counts
    cursor.execute('''
        SELECT t.topicID, t.title, t.content, t.creationTime,
               u.userName,
               (SELECT COUNT(*) FROM comment WHERE topicID = t.topicID) as commentCount,
               (SELECT COUNT(*) FROM likes WHERE targetType = 'topic' AND targetID = t.topicID) as likeCount,
               EXISTS(
                   SELECT 1 FROM likes 
                   WHERE targetType = 'topic' 
                   AND targetID = t.topicID 
                   AND userID = ?
               ) as userLiked
        FROM topic t
        JOIN user u ON t.postingUser = u.userID
        ORDER BY t.creationTime DESC
    ''', (session.get('user_id', -1),))
    topics = [dict(row) for row in cursor.fetchall()]
    
    return render_template('Homepage.html', topics=topics, logged_in=logged_in)


@app.route('/topic/<int:topic_id>')
def view_topic(topic_id):
    logged_in = is_logged_in()
    db = get_db()
    cursor = db.cursor()
    
    # Get topic details with like count
    cursor.execute('''
        SELECT t.*, u.userName,
               (SELECT COUNT(*) FROM likes WHERE targetType = 'topic' AND targetID = t.topicID) as likeCount,
               EXISTS(
                   SELECT 1 FROM likes 
                   WHERE targetType = 'topic' 
                   AND targetID = t.topicID 
                   AND userID = ?
               ) as userLiked
        FROM topic t
        JOIN user u ON t.postingUser = u.userID
        WHERE t.topicID = ?
        GROUP BY t.topicID
    ''', (session.get('user_id', -1), topic_id))
    topic = cursor.fetchone()
    
    if not topic:
        return 'Topic not found', 404
    
    # Get all comments for this topic with like counts
    cursor.execute('''
        SELECT c.*, u.userName,
               (SELECT COUNT(*) FROM likes WHERE targetType = 'comment' AND targetID = c.commentID) as likeCount,
               EXISTS(
                   SELECT 1 FROM likes 
                   WHERE targetType = 'comment' 
                   AND targetID = c.commentID 
                   AND userID = ?
               ) as userLiked
        FROM comment c
        JOIN user u ON c.postingUser = u.userID
        WHERE c.topicID = ? AND c.parentCommentID IS NULL
        ORDER BY c.creationTime DESC
    ''', (session.get('user_id', -1), topic_id))
    comments = [dict(row) for row in cursor.fetchall()]
    
    # Get replies for each comment
    for comment in comments:
        comment['replies'] = get_nested_replies(comment['commentID'])
    
    return render_template('topic.html', topic=dict(topic), comments=comments, logged_in=logged_in)


def get_nested_replies(comment_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT c.*, u.userName,
               (SELECT COUNT(*) FROM likes WHERE targetType = 'comment' AND targetID = c.commentID) as likeCount,
               EXISTS(
                   SELECT 1 FROM likes 
                   WHERE targetType = 'comment' 
                   AND targetID = c.commentID 
                   AND userID = ?
               ) as userLiked
        FROM comment c
        JOIN user u ON c.postingUser = u.userID
        WHERE c.parentCommentID = ?
        ORDER BY c.creationTime ASC
    ''', (session.get('user_id', -1), comment_id))
    replies = [dict(row) for row in cursor.fetchall()]
    
    # Recursively get nested replies
    for reply in replies:
        reply['replies'] = get_nested_replies(reply['commentID'])
    
    return replies


@app.route('/create-topic', methods=['POST'])
@login_required
def create_topic():
    title = request.form.get('title')
    content = request.form.get('content', '')
    
    if not title:
        flash('Title is required', 'error')
        return redirect(url_for('create_page'))
    
    try:
        db = get_db()
        cursor = db.cursor()
        now = datetime.datetime.now()
        
        # Get the username for the current user
        cursor.execute('SELECT userName FROM user WHERE userID = ?', (session['user_id'],))
        user = cursor.fetchone()
        
        cursor.execute('''
            INSERT INTO topic (title, content, postingUser, creationTime, updateTime)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, session['user_id'], now, now))
        
        topic_id = cursor.lastrowid
        db.commit()
        
        return redirect(url_for('view_topic', topic_id=topic_id))
    except Exception as e:
        db.rollback()
        flash('Error creating topic: ' + str(e), 'error')
        return redirect(url_for('create_page'))


@app.route('/add-comment', methods=['POST'])
@login_required
def add_comment():
    content = request.form.get('content')
    topic_id = request.form.get('topicId')
    parent_id = request.form.get('parentId')  # Optional, for replies
    
    if not content or not topic_id:
        flash('Missing required data', 'error')
        return redirect(url_for('view_topic', topic_id=topic_id))
    
    try:
        db = get_db()
        cursor = db.cursor()
        now = datetime.datetime.now()
        
        # Get the username for the current user
        cursor.execute('SELECT userName FROM user WHERE userID = ?', (session['user_id'],))
        user = cursor.fetchone()
        
        cursor.execute('''
            INSERT INTO comment (content, postingUser, topicID, parentCommentID, creationTime, updateTime)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (content, session['user_id'], topic_id, parent_id, now, now))
        
        db.commit()
        return redirect(url_for('view_topic', topic_id=topic_id))
    except Exception as e:
        db.rollback()
        flash('Error adding comment: ' + str(e), 'error')
        return redirect(url_for('view_topic', topic_id=topic_id))


# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT userID, userName, passwordHash 
        FROM user 
        WHERE userName = ?
    ''', (username,))
    user = cursor.fetchone()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['passwordHash']):
        session['username'] = user['userName']
        session['user_id'] = user['userID']
        return redirect(url_for('home'))
    else:
        flash('Invalid username or password', 'error')
        return redirect(url_for('home'))


# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    fullname = request.form['fullname']
    email = request.form['email']
    
    if not username or not password or not fullname or not email:
        flash('All fields are required', 'error')
        return redirect(url_for('home'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if username already exists
    cursor.execute('SELECT 1 FROM user WHERE userName = ?', (username,))
    if cursor.fetchone():
        flash('Username already exists', 'error')
        return redirect(url_for('home'))
    
    try:
        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Insert new user
        cursor.execute('''
            INSERT INTO user (userName, passwordHash, fullName, email)
            VALUES (?, ?, ?, ?)
        ''', (username, hashed_password, fullname, email))
        
        db.commit()
        
        # Log the user in
        cursor.execute('SELECT userID, userName FROM user WHERE userName = ?', (username,))
        user = cursor.fetchone()
        session['username'] = user['userName']
        session['user_id'] = user['userID']
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        db.rollback()
        flash('Error creating account: ' + str(e), 'error')
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/create', methods=['GET'])
def create_page():
    if not is_logged_in():
        return redirect(url_for('home'))
    return render_template('create.html', logged_in=True)


@app.route('/like', methods=['POST'])
@login_required
def toggle_like():
    target_type = request.form.get('targetType')  # 'topic' or 'comment'
    target_id = request.form.get('targetId')
    
    if not target_type or not target_id or target_type not in ('topic', 'comment'):
        flash('Invalid request', 'error')
        return redirect(request.referrer or url_for('home'))
    
    try:
        db = get_db()
        cursor = db.cursor()
        now = datetime.datetime.now()
        
        # Check if like exists
        cursor.execute('''
            SELECT likeID FROM likes 
            WHERE userID = ? AND targetType = ? AND targetID = ?
        ''', (session['user_id'], target_type, target_id))
        existing_like = cursor.fetchone()
        
        if existing_like:
            # Unlike
            cursor.execute('''
                DELETE FROM likes 
                WHERE userID = ? AND targetType = ? AND targetID = ?
            ''', (session['user_id'], target_type, target_id))
        else:
            # Like
            cursor.execute('''
                INSERT INTO likes (userID, targetType, targetID, creationTime)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], target_type, target_id, now))
        
        db.commit()
        
        # Redirect back to the page they were on
        return redirect(request.referrer or url_for('home'))
    except Exception as e:
        db.rollback()
        flash('Error toggling like: ' + str(e), 'error')
        return redirect(request.referrer or url_for('home'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
