from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, flash, send_from_directory
import sqlite3
from datetime import datetime
import os
import bcrypt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['DATABASE'] = 'debate.sqlite'
app.secret_key = 'your_secret_key'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    get_db().commit()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def is_logged_in():
    return 'user_id' in session


def get_current_user():
    if 'user_id' in session:
        user_query = "SELECT userName FROM user WHERE userID = ?"
        user = query_db(user_query, [session['user_id']], one=True)
        return user['userName'] if user else None
    return None


@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())


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


# Format timestamp to show only hours and minutes
def format_timestamp(timestamp):
    if isinstance(timestamp, str):
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    else:
        dt = timestamp
    return dt.strftime('%I:%M %p')  # 12-hour format with AM/PM


def format_datetime(timestamp):
    """Helper function to format datetime consistently"""
    if isinstance(timestamp, str):
        # If timestamp is already a string, parse it first
        try:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return timestamp  # Return as is if parsing fails
    else:
        dt = timestamp
    return dt.strftime('%I:%M %p, %b %d, %Y')


# Display homepage
@app.route('/')
def home():
    if is_logged_in():
        query = """
            SELECT t.*,
                   u.userName,
                   strftime('%Y-%m-%d %H:%M:%S.000', t.creationTime) as creationTime,
                   COUNT(DISTINCT c.commentID) as commentCount,
                   COUNT(DISTINCT l.likeID) as likeCount,
                   EXISTS(
                       SELECT 1 FROM likes 
                       WHERE targetID = t.topicID 
                       AND targetType = 'topic' 
                       AND userID = ?
                   ) as userLiked
            FROM topic t
            JOIN user u ON t.postingUser = u.userID
            LEFT JOIN comment c ON t.topicID = c.topicID
            LEFT JOIN likes l ON t.topicID = l.targetID AND l.targetType = 'topic'
            GROUP BY t.topicID
            ORDER BY t.creationTime DESC
        """
        topics = query_db(query, [session.get('user_id')])
    else:
        query = """
            SELECT t.*,
                   u.userName,
                   strftime('%Y-%m-%d %H:%M:%S.000', t.creationTime) as creationTime,
                   COUNT(DISTINCT c.commentID) as commentCount,
                   COUNT(DISTINCT l.likeID) as likeCount
            FROM topic t
            JOIN user u ON t.postingUser = u.userID
            LEFT JOIN comment c ON t.topicID = c.topicID
            LEFT JOIN likes l ON t.topicID = l.targetID AND l.targetType = 'topic'
            GROUP BY t.topicID
            ORDER BY t.creationTime DESC
        """
        topics = query_db(query)

    # Convert rows to dictionaries and format timestamps
    formatted_topics = []
    for topic in topics:
        topic_dict = dict(topic)
        topic_dict['creationTime'] = format_datetime(topic_dict['creationTime'])
        formatted_topics.append(topic_dict)

    return render_template('Homepage.html', topics=formatted_topics, logged_in=is_logged_in())


@app.route('/topic/<int:topic_id>')
def view_topic(topic_id):
    # Get topic details with formatted timestamp
    topic_query = """
        SELECT t.*,
               u.userName,
               strftime('%Y-%m-%d %H:%M:%S.000', t.creationTime) as creationTime,
               EXISTS(
                   SELECT 1 FROM likes 
                   WHERE targetID = t.topicID 
                   AND targetType = 'topic' 
                   AND userID = ?
               ) as userLiked,
               (SELECT COUNT(*) FROM likes WHERE targetID = t.topicID AND targetType = 'topic') as likeCount
        FROM topic t
        JOIN user u ON t.postingUser = u.userID
        WHERE t.topicID = ?
    """
    topic = query_db(topic_query, [session.get('user_id', -1), topic_id], one=True)
    
    if not topic:
        flash('Topic not found', 'error')
        return redirect(url_for('home'))

    # Convert topic to dictionary and format timestamp
    topic_dict = dict(topic)
    topic_dict['creationTime'] = format_datetime(topic_dict['creationTime'])

    # Get comments with formatted timestamps
    comments_query = """
        SELECT c.*,
               u.userName,
               strftime('%Y-%m-%d %H:%M:%S.000', c.creationTime) as creationTime,
               EXISTS(
                   SELECT 1 FROM likes 
                   WHERE targetID = c.commentID 
                   AND targetType = 'comment' 
                   AND userID = ?
               ) as userLiked,
               (SELECT COUNT(*) FROM likes WHERE targetID = c.commentID AND targetType = 'comment') as likeCount
        FROM comment c
        JOIN user u ON c.postingUser = u.userID
        WHERE c.topicID = ? AND c.parentCommentID IS NULL
        ORDER BY c.creationTime DESC
    """
    comments = query_db(comments_query, [session.get('user_id', -1), topic_id])

    # Convert comments to dictionaries and format timestamps
    formatted_comments = []
    for comment in comments:
        comment_dict = dict(comment)
        comment_dict['creationTime'] = format_datetime(comment_dict['creationTime'])
        
        # Get replies with formatted timestamps
        replies_query = """
            SELECT c.*,
                   u.userName,
                   strftime('%Y-%m-%d %H:%M:%S.000', c.creationTime) as creationTime,
                   EXISTS(
                       SELECT 1 FROM likes 
                       WHERE targetID = c.commentID 
                       AND targetType = 'comment' 
                       AND userID = ?
                   ) as userLiked,
                   (SELECT COUNT(*) FROM likes WHERE targetID = c.commentID AND targetType = 'comment') as likeCount
            FROM comment c
            JOIN user u ON c.postingUser = u.userID
            WHERE c.parentCommentID = ?
            ORDER BY c.creationTime ASC
        """
        replies = query_db(replies_query, [session.get('user_id', -1), comment_dict['commentID']])
        
        # Convert replies to dictionaries and format timestamps
        formatted_replies = []
        for reply in replies:
            reply_dict = dict(reply)
            reply_dict['creationTime'] = format_datetime(reply_dict['creationTime'])
            formatted_replies.append(reply_dict)
        
        comment_dict['replies'] = formatted_replies
        formatted_comments.append(comment_dict)

    return render_template('topic.html', topic=topic_dict, comments=formatted_comments, logged_in=is_logged_in())


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
    stance = request.form.get('stance')  # Get the stance from the form
    
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
            INSERT INTO comment (content, postingUser, topicID, parentCommentID, stance, creationTime, updateTime)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (content, session['user_id'], topic_id, parent_id, stance, now, now))
        
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


@app.route('/api/filter-topics')
def filter_topics():
    # Get filter parameters
    sort_by = request.args.get('sortBy', 'newest')
    stance = request.args.get('stance', 'all')
    user = request.args.get('user', '')
    date_from = request.args.get('dateFrom', '')
    date_to = request.args.get('dateTo', '')
    popularity = request.args.get('popularity', 'all')
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Base query with proper column selection
        query = """
            SELECT 
                t.topicID,
                t.title,
                t.content,
                strftime('%I:%M %p', t.creationTime) as creationTime,
                u.userName,
                (SELECT COUNT(*) FROM comment WHERE topicID = t.topicID) as commentCount,
                (SELECT COUNT(*) FROM likes WHERE targetID = t.topicID AND targetType = 'topic') as likeCount,
                EXISTS(
                    SELECT 1 FROM likes 
                    WHERE targetID = t.topicID 
                    AND targetType = 'topic' 
                    AND userID = ?
                ) as userLiked
            FROM topic t
            LEFT JOIN user u ON t.postingUser = u.userID
            WHERE 1=1
        """
        params = [session.get('user_id', -1)]
        
        # Add filters
        if stance != 'all':
            query += " AND t.stance = ?"
            params.append(stance)
        
        if user:
            query += " AND u.userName LIKE ?"
            params.append(f"%{user}%")
        
        if date_from:
            query += " AND DATE(t.creationTime) >= DATE(?)"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(t.creationTime) <= DATE(?)"
            params.append(date_to)
        
        # Add popularity filter using subquery
        if popularity != 'all':
            like_count_query = "(SELECT COUNT(*) FROM likes WHERE targetID = t.topicID AND targetType = 'topic')"
            if popularity == 'high':
                query += f" AND {like_count_query} > 10"
            elif popularity == 'medium':
                query += f" AND {like_count_query} BETWEEN 5 AND 10"
            else:  # low
                query += f" AND {like_count_query} < 5"
        
        # Add sorting
        if sort_by == 'newest':
            query += " ORDER BY t.creationTime DESC"
        elif sort_by == 'oldest':
            query += " ORDER BY t.creationTime ASC"
        elif sort_by == 'most_liked':
            query += " ORDER BY likeCount DESC"
        elif sort_by == 'most_replied':
            query += " ORDER BY commentCount DESC"
        
        # Execute query
        cursor.execute(query, params)
        topics = cursor.fetchall()
        
        # Convert to list of dicts with proper column mapping
        topics_list = []
        for topic in topics:
            topics_list.append({
                'topicID': topic[0],
                'title': topic[1],
                'content': topic[2],
                'creationTime': topic[3],
                'userName': topic[4],
                'commentCount': topic[5],
                'likeCount': topic[6],
                'userLiked': bool(topic[7]),
                'isLoggedIn': 'user_id' in session
            })
        
        return jsonify({'success': True, 'topics': topics_list})
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/profile/<username>')
def view_profile(username):
    if not username:
        return redirect(url_for('home'))

    # Get user info with formatted join date
    user_query = """
        SELECT userID, 
               userName, 
               strftime('%I:%M %p, %b %d, %Y', creationTime) as joinDate
        FROM user 
        WHERE userName = ?
    """
    user = query_db(user_query, [username], one=True)
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('home'))

    # Convert user to dictionary
    user_dict = dict(user)

    # Get user's topics with formatted timestamps
    topics_query = """
        SELECT t.*, 
               strftime('%Y-%m-%d %H:%M:%S.000', t.creationTime) as creationTime,
               COUNT(DISTINCT c.commentID) as commentCount,
               COUNT(DISTINCT l.likeID) as likeCount
        FROM topic t
        LEFT JOIN comment c ON t.topicID = c.topicID
        LEFT JOIN likes l ON t.topicID = l.targetID AND l.targetType = 'topic'
        WHERE t.postingUser = ?
        GROUP BY t.topicID
        ORDER BY t.creationTime DESC
    """
    topics = query_db(topics_query, [user_dict['userID']])

    # Convert topics to dictionaries and format timestamps
    formatted_topics = []
    for topic in topics:
        topic_dict = dict(topic)
        topic_dict['creationTime'] = format_datetime(topic_dict['creationTime'])
        formatted_topics.append(topic_dict)

    # Get user's comments with formatted timestamps
    comments_query = """
        SELECT c.*,
               t.title as topicTitle,
               strftime('%Y-%m-%d %H:%M:%S.000', c.creationTime) as creationTime,
               COUNT(l.likeID) as likeCount
        FROM comment c
        JOIN topic t ON c.topicID = t.topicID
        LEFT JOIN likes l ON c.commentID = l.targetID AND l.targetType = 'comment'
        WHERE c.postingUser = ?
        GROUP BY c.commentID
        ORDER BY c.creationTime DESC
    """
    comments = query_db(comments_query, [user_dict['userID']])

    # Convert comments to dictionaries and format timestamps
    formatted_comments = []
    for comment in comments:
        comment_dict = dict(comment)
        comment_dict['creationTime'] = format_datetime(comment_dict['creationTime'])
        formatted_comments.append(comment_dict)

    # Calculate stance statistics
    stance_query = """
        SELECT stance, COUNT(*) as count
        FROM comment
        WHERE postingUser = ? AND stance IS NOT NULL
        GROUP BY stance
    """
    stance_counts = query_db(stance_query, [user_dict['userID']])
    
    total_comments = sum(count['count'] for count in stance_counts)
    supporting_count = next((item['count'] for item in stance_counts if item['stance'] == 'supporting'), 0)
    opposed_count = next((item['count'] for item in stance_counts if item['stance'] == 'opposed'), 0)
    
    stance_stats = {
        'total_comments': total_comments,
        'supporting_percentage': round((supporting_count / total_comments * 100) if total_comments > 0 else 0),
        'opposed_percentage': round((opposed_count / total_comments * 100) if total_comments > 0 else 0)
    }

    return render_template('profile.html',
                         user=user_dict,
                         topics=formatted_topics,
                         comments=formatted_comments,
                         stance_stats=stance_stats,
                         logged_in=is_logged_in())


@app.route('/apply_filters', methods=['POST'])
def apply_filters():
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    # Get filter parameters
    sort_by = request.form.get('sortBy', 'newest')
    stance = request.form.get('stance', 'all')
    user_filter = request.form.get('user', '')
    date_from = request.form.get('dateFrom', '')
    date_to = request.form.get('dateTo', '')
    popularity = request.form.get('popularity', 'all')

    # Build the base query with formatted timestamp
    query = """
        SELECT t.*, 
               u.userName,
               strftime('%Y-%m-%d %H:%M:%S.000', t.creationTime) as creationTime,
               COUNT(DISTINCT c.commentID) as commentCount,
               COUNT(DISTINCT l.likeID) as likeCount,
               EXISTS(
                   SELECT 1 FROM likes 
                   WHERE targetID = t.topicID 
                   AND targetType = 'topic' 
                   AND userID = ?
               ) as userLiked
        FROM topic t
        JOIN user u ON t.postingUser = u.userID
        LEFT JOIN comment c ON t.topicID = c.topicID
        LEFT JOIN likes l ON t.topicID = l.targetID AND l.targetType = 'topic'
    """

    params = [session.get('user_id')]
    where_clauses = []

    # Add stance filter
    if stance != 'all':
        where_clauses.append("EXISTS (SELECT 1 FROM comment WHERE topicID = t.topicID AND stance = ?)")
        params.append(stance)

    # Add user filter
    if user_filter:
        where_clauses.append("u.userName LIKE ?")
        params.append(f"%{user_filter}%")

    # Add date range filter
    if date_from:
        where_clauses.append("DATE(t.creationTime) >= DATE(?)")
        params.append(date_from)
    if date_to:
        where_clauses.append("DATE(t.creationTime) <= DATE(?)")
        params.append(date_to)

    # Add popularity filter
    if popularity != 'all':
        if popularity == 'high':
            where_clauses.append("(SELECT COUNT(*) FROM likes WHERE targetID = t.topicID AND targetType = 'topic') > 10")
        elif popularity == 'medium':
            where_clauses.append("(SELECT COUNT(*) FROM likes WHERE targetID = t.topicID AND targetType = 'topic') BETWEEN 5 AND 10")
        elif popularity == 'low':
            where_clauses.append("(SELECT COUNT(*) FROM likes WHERE targetID = t.topicID AND targetType = 'topic') < 5")

    # Add WHERE clause if there are any conditions
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # Add GROUP BY
    query += " GROUP BY t.topicID"

    # Add ORDER BY based on sort_by parameter
    if sort_by == 'newest':
        query += " ORDER BY t.creationTime DESC"
    elif sort_by == 'oldest':
        query += " ORDER BY t.creationTime ASC"
    elif sort_by == 'most_liked':
        query += " ORDER BY likeCount DESC, t.creationTime DESC"
    elif sort_by == 'most_replied':
        query += " ORDER BY commentCount DESC, t.creationTime DESC"

    try:
        # Execute query and get results
        topics = query_db(query, params)
        
        # Format timestamps
        formatted_topics = []
        for topic in topics:
            formatted_topic = dict(topic)
            formatted_topic['creationTime'] = format_datetime(topic['creationTime'])
            formatted_topics.append(formatted_topic)

        return jsonify({
            'success': True,
            'topics': formatted_topics
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
