-- Drop existing tables if they exist
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS topic;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS likes;

-- Create user table
CREATE TABLE user (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    userName TEXT UNIQUE NOT NULL,
    passwordHash TEXT NOT NULL,
    isAdmin INTEGER DEFAULT 0,
    creationTime DATETIME NOT NULL,
    lastVisit DATETIME NOT NULL
);

-- Create topic table (equivalent to Reddit posts)
CREATE TABLE topic (
    topicID INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    postingUser INTEGER NOT NULL,
    creationTime DATETIME NOT NULL,
    updateTime DATETIME NOT NULL,
    FOREIGN KEY (postingUser) REFERENCES user(userID)
);

-- Create comment table (for both top-level comments and replies)
CREATE TABLE comment (
    commentID INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    postingUser INTEGER NOT NULL,
    topicID INTEGER NOT NULL,
    parentCommentID INTEGER DEFAULT NULL, -- NULL means it's a top-level comment
    creationTime DATETIME NOT NULL,
    updateTime DATETIME NOT NULL,
    FOREIGN KEY (postingUser) REFERENCES user(userID),
    FOREIGN KEY (topicID) REFERENCES topic(topicID),
    FOREIGN KEY (parentCommentID) REFERENCES comment(commentID)
);

-- Create likes table (for both topics and comments)
CREATE TABLE likes (
    likeID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    targetType TEXT NOT NULL CHECK (targetType IN ('topic', 'comment')),
    targetID INTEGER NOT NULL,
    creationTime DATETIME NOT NULL,
    FOREIGN KEY (userID) REFERENCES user(userID),
    UNIQUE(userID, targetType, targetID)
);

-- Create indexes for better performance
CREATE INDEX idx_comment_topic ON comment(topicID);
CREATE INDEX idx_comment_parent ON comment(parentCommentID);
CREATE INDEX idx_comment_user ON comment(postingUser);

-- Create indexes for likes
CREATE INDEX idx_likes_user ON likes(userID);
CREATE INDEX idx_likes_target ON likes(targetType, targetID); 