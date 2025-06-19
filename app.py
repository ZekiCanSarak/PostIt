from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import sqlite3
import datetime

app = Flask(__name__)
app.config['DATABASE'] = 'debate.sqlite'
app.secret_key = 'your_secret_key'


def get_db():
    db = sqlite3.connect('debate.sqlite')
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def is_logged_in():
    return 'username' in session

# Display homepage
@app.route('/')
def home():
    logged_in = is_logged_in()
    topics_with_claims = []
    if logged_in:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT topicID, topicName, postingUser, strftime("%Y-%m-%d %H:%M:%S", creationTime) as formattedCreationTime FROM topic ORDER BY creationTime DESC')
        topics = [dict(topic) for topic in cursor.fetchall()]
        for topic in topics:
            cursor.execute("""
                SELECT claimID, postingUser, text, strftime("%Y-%m-%d %H:%M:%S", creationTime) as formattedCreationTime
                FROM claim
                WHERE topic = ?
                ORDER BY creationTime DESC
            """, (topic['topicID'],))
            claims = [dict(claim) for claim in cursor.fetchall()]
            for claim in claims:
                cursor.execute("""
                    SELECT rt.replyTextID, rt.text, u.userName, strftime("%Y-%m-%d %H:%M:%S", rt.creationTime) as formattedCreationTime
                    FROM replyText rt
                    JOIN user u ON rt.postingUser = u.userID
                    JOIN replyToClaim rtc ON rt.replyTextID = rtc.reply
                    WHERE rtc.claim = ?
                    ORDER BY rt.creationTime
                """, (claim['claimID'],))
                replies = [dict(reply) for reply in cursor.fetchall()]
                claim['replies'] = replies
            topics_with_claims.append((topic, claims))
    return render_template('Homepage.html', topics=topics_with_claims, logged_in=logged_in)







@app.route('/create', methods=['GET'])
def create_page():
    if is_logged_in():
        return render_template('create.html')
    else:
        return redirect(url_for('home', message='Please login to access this page.'))
    

    

@app.route('/get-claims/<int:topic_id>')
def get_claims(topic_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT c.claimID, c.userID, c.text, u.userName, c.creationTime
        FROM claim c
        JOIN user u ON c.postingUser = u.userID
        WHERE c.topic = ?
        ORDER BY c.creationTime DESC
    """, (topic_id,))
    claims = cursor.fetchall()
    return jsonify(claims)



@app.route('/add-reply', methods=['POST'])
def add_reply():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User must be logged in to add replies.'}), 401

    text = request.form.get('text')
    claim_id = request.form.get('claimId')  
    user_id = session.get('user_id')
    username = session.get('username')  

    if not text or not claim_id:
        return jsonify({'success': False, 'message': 'Missing required data.'}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO replyText (postingUser, text, creationTime) 
            VALUES (?, ?, datetime('now'))
        """, (user_id, text))
        reply_id = cursor.lastrowid  

        
        cursor.execute("""
            INSERT INTO replyToClaim (reply, claim, replyToClaimRelType) 
            VALUES (?, ?, ?)
        """, (reply_id, claim_id, 1))  
        db.commit()

        return jsonify({'success': True, 'message': 'Reply added successfully', 'username': username})
    except Exception as e:
        db.rollback()
        print(e)
        return jsonify({'success': False, 'message': 'Failed to add reply.'}), 500
    

@app.route('/reply-to-reply', methods=['POST'])
def reply_to_reply():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User must be logged in to add replies.'}), 401

    text = request.form.get('text')
    parent_reply_id = request.form.get('replyToReplyID')  
    user_id = session.get('user_id')

    if not text or not parent_reply_id:
        return jsonify({'success': False, 'message': 'Missing required data.'}), 400

    try:
        db = get_db()
        cursor = db.cursor()
       
        cursor.execute("""
            INSERT INTO replyText (postingUser, text, creationTime) 
            VALUES (?, ?, datetime('now'))
        """, (user_id, text))
        new_reply_id = cursor.lastrowid  

        
        cursor.execute("""
            INSERT INTO replyToReply (reply, parent, replyToReplyRelType) 
            VALUES (?, ?, ?)
        """, (new_reply_id, parent_reply_id, 1))  

        db.commit()

        return jsonify({'success': True, 'message': 'Reply added successfully', 'username': session.get('username')})
    except Exception as e:
        db.rollback()
        print(e)
        return jsonify({'success': False, 'message': 'Failed to add reply: ' + str(e)}), 500


    

@app.route('/get-replies/<int:claim_id>')
def get_replies(claim_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT rt.replyTextID, rt.text, u.userName, rt.creationTime
        FROM replyText rt
        JOIN user u ON rt.postingUser = u.userID
        JOIN replyToClaim rtc ON rt.replyTextID = rtc.reply
        WHERE rtc.claim = ?
        ORDER BY rt.creationTime
    """, (claim_id,))
    replies = [dict(reply) for reply in cursor.fetchall()]

    for reply in replies:
        cursor.execute("""
            SELECT rt.replyTextID, rt.text, u.userName, rt.creationTime
            FROM replyText rt
            JOIN user u ON rt.postingUser = u.userID
            JOIN replyToReply rtr ON rt.replyTextID = rtr.reply
            WHERE rtr.parent = ?
            ORDER BY rt.creationTime
        """, (reply['replyTextID'],))
        nested_replies = [dict(nested_reply) for nested_reply in cursor.fetchall()]
        reply['nested_replies'] = nested_replies

    return jsonify(replies)





    
@app.route('/create-claim', methods=['POST'])
def create_claim():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'User must be logged in to submit claims.'}), 401
    topic = request.form.get('topic')
    text = request.form.get('text')
    posting_user = session['username']  
    print("Received claim:", text, "for topic:", topic)  

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO claim (topic, postingUser, creationTime, updateTime, text) VALUES (?, ?, ?, ?, ?)',
                           (topic, posting_user, datetime.datetime.now(), datetime.datetime.now(), text))
            conn.commit()
        
            new_claim_id = cursor.lastrowid  
            return jsonify({'success': True, 'message': 'Claim created successfully', 'claimId': new_claim_id, 'claimText': text})

    except Exception as e:
        print("Error inserting claim:", e)  
        return jsonify({'success': False, 'message': 'Failed to create claim.'}), 500


    

@app.route('/create-topic', methods=['GET', 'POST'])
def create_topic():
    if request.method == 'POST':
        
        if is_logged_in():
            topic_name = request.form['topic']
            posting_user = session['username']
            
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO topic (topicName, postingUser, creationTime, updateTime) VALUES (?, ?, ?, ?)',
                               (topic_name, posting_user, current_time, current_time))
                conn.commit()

            return jsonify({'success': True, 'message': 'Topic created successfully'})
        else:
            return redirect(url_for('login'))
    else:
        
        return render_template('create.html')
    


@app.route('/create-post', methods=['GET'])
def create_post():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    return render_template('create.html')  




@app.route('/topic/<int:topic_id>')
def view_topic(topic_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM topic WHERE topicID = ?', (topic_id,))
        topic = cursor.fetchone()
    if topic:
        return render_template('Homepage.html', topic=topic)
    else:
        return 'Topic not found', 404
    

    
@app.route('/create-claim-to-claim', methods=['POST'])
def create_claim_to_claim():
    if not 'username' in session:
        return jsonify({'success': False, 'message': 'User must be logged in to submit relationships.'}), 401
    first_claim_id = request.form.get('firstClaimId')
    second_claim_id = request.form.get('secondClaimId')
    relation_type = request.form.get('relationType')

    if not all([first_claim_id, second_claim_id, relation_type]):
        return jsonify({'success': False, 'message': 'Missing required data.'}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO claimToClaim (first, second, claimRelType) VALUES (?, ?, ?)
        """, (first_claim_id, second_claim_id, relation_type))
        db.commit()
        return jsonify({'success': True, 'message': 'Claim relationship added successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Failed to add claim relationship: ' + str(e)}), 500




# Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT userID, passwordHash FROM user WHERE userName = ?", (username,))
    user = cursor.fetchone()
    
    if user and user['passwordHash'] == password:  
        session['username'] = username
        session['user_id'] = user['userID']
        return redirect(url_for('home'))  
    else:
        return redirect(url_for('home'))  



# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        if password != password_confirm:
            
            return jsonify({'success': False, 'message': 'Passwords do not match'})

        db = get_db()
        cursor = db.cursor()
        
        
        cursor.execute('SELECT * FROM user WHERE userName=?', (username,))
        if cursor.fetchone():
            
            return jsonify({'success': False, 'message': 'Username already exists'})
        current_time = datetime.datetime.now()

        
        cursor.execute("""
            INSERT INTO user (userName, passwordHash, isAdmin, creationTime, lastVisit)
            VALUES (?, ?, 0, ?, ?)
        """, (username, password, current_time, current_time))
        db.commit()
        
        
        return redirect(url_for('home'))
    
@app.route('/get-nested-replies/<int:parent_reply_id>')
def get_nested_replies(parent_reply_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT rt.replyTextID, rt.text, u.userName, strftime('%Y-%m-%d %H:%M:%S', rt.creationTime) as formattedCreationTime
        FROM replyText rt
        JOIN user u ON rt.postingUser = u.userID
        JOIN replyToReply rtr ON rt.replyTextID = rtr.reply
        WHERE rtr.parent = ?
        ORDER BY rt.creationTime DESC
    """, (parent_reply_id,))
    nested_replies = [dict(reply) for reply in cursor.fetchall()]
    return jsonify(nested_replies)

    



# User logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
