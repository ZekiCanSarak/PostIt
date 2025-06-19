BEGIN TRANSACTION;
CREATE TABLE claim (
    claimID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,   -- CLaim ID number
    topic INTEGER NOT NULL REFERENCES topic(topicID) ON DELETE CASCADE ON UPDATE CASCADE, -- FK of claim
    postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE, -- FK of poisting user
    creationTime INTEGER NOT NULL,                       -- Time topic was created
    updateTime INTEGER NOT NULL,                         -- Last time a reply was added
    text TEXT NOT NULL                                   -- Actual text
);
INSERT INTO "claim" VALUES(1,3,'zeki','2024-04-17 21:55:39.951833','2024-04-17 21:55:39.951854','Colours of the rainbow');
INSERT INTO "claim" VALUES(2,2,'zeki','2024-04-17 21:57:17.934239','2024-04-17 21:57:17.934254','Testing websites');
INSERT INTO "claim" VALUES(3,3,'zeki','2024-04-17 22:02:13.446790','2024-04-17 22:02:13.446811','Fein');
INSERT INTO "claim" VALUES(4,2,'zeki','2024-04-17 22:02:33.658552','2024-04-17 22:02:33.658576','Testing websites are fun');
INSERT INTO "claim" VALUES(5,3,'zeki','2024-04-17 23:32:26.204180','2024-04-17 23:32:26.204198','Colour');
INSERT INTO "claim" VALUES(6,4,'zeki','2024-04-18 00:49:19.697856','2024-04-18 00:49:19.697874','I think the best game ever to exist is CS:GO');
INSERT INTO "claim" VALUES(7,4,'zeki','2024-04-19 01:10:25.368758','2024-04-19 01:10:25.368781','Solitare');
INSERT INTO "claim" VALUES(8,5,'x31canavari69x','2024-04-19 23:41:34.844198','2024-04-19 23:41:34.844213','Champions League is the most competitive tournament');
INSERT INTO "claim" VALUES(9,1,'zeki','2024-04-20 13:16:07.382789','2024-04-20 13:16:07.382806','would win superlig');
INSERT INTO "claim" VALUES(10,6,'zeki','2024-04-20 13:32:51.408991','2024-04-20 13:32:51.409016','Mid Uni');
INSERT INTO "claim" VALUES(11,6,'zeki','2024-04-21 14:49:45.194905','2024-04-21 14:49:45.194921','yo');
INSERT INTO "claim" VALUES(12,6,'zeki','2024-04-21 14:50:09.533380','2024-04-21 14:50:09.533399','wd');
INSERT INTO "claim" VALUES(13,6,'zeki','2024-04-21 14:50:35.727301','2024-04-21 14:50:35.727319','awd');
INSERT INTO "claim" VALUES(14,7,'zeki','2024-04-22 17:44:54.901236','2024-04-22 17:44:54.901256','I agree it can increase you understanding and also focus');
INSERT INTO "claim" VALUES(15,7,'x31canavari69x','2024-04-23 22:20:34.100221','2024-04-23 22:20:34.100242','I think it does not according to the latest researches made');
INSERT INTO "claim" VALUES(16,1,'zeki','2024-04-28 19:26:06.682147','2024-04-28 19:26:06.682165','galatasaray is the greatest team ever in superlig');
CREATE TABLE claimToClaim (
    claimRelID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,                        -- Claim relationship ID
    first INTEGER NOT NULL REFERENCES claim(claimID) ON DELETE CASCADE ON UPDATE CASCADE, -- FK of first related claim
    second INTEGER NOT NULL REFERENCES claim(claimID) ON DELETE CASCADE ON UPDATE CASCADE, -- FK of second related claim
    claimRelType INTEGER NOT NULL REFERENCES claimToClaimType(claimRelTypeID) ON DELETE CASCADE ON UPDATE CASCADE,
                                                                                            -- FK of type of relation
    /* Specify that there can't be several relationships between the same pair of two claims */
    CONSTRAINT claimToClaimUnique UNIQUE (first, second)
);
INSERT INTO "claimToClaim" VALUES(1,14,13,1);
INSERT INTO "claimToClaim" VALUES(2,15,14,1);
CREATE TABLE claimToClaimType (
    claimRelTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    claimRelType TEXT NOT NULL
);
INSERT INTO "claimToClaimType" VALUES(1,'Opposed');
INSERT INTO "claimToClaimType" VALUES(2,'Equivalent');
CREATE TABLE replyText (
    replyTextID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,                           -- Reply ID
    postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE, -- FK of posting user
    creationTime INTEGER NOT NULL,                                                    -- Posting time
    text TEXT NOT NULL                                                                -- Text of reply
);
INSERT INTO "replyText" VALUES(1,1,'2024-04-18 16:48:02','it is a great game');
INSERT INTO "replyText" VALUES(2,1,'2024-04-18 16:52:34','I played that game a lot back in the day');
INSERT INTO "replyText" VALUES(3,1,'2024-04-18 16:53:29','great game');
INSERT INTO "replyText" VALUES(4,1,'2024-04-18 16:53:44','yes it is');
INSERT INTO "replyText" VALUES(5,1,'2024-04-18 16:57:38','great game');
INSERT INTO "replyText" VALUES(6,1,'2024-04-18 17:03:47','yeah I used to play it a lot');
INSERT INTO "replyText" VALUES(7,1,'2024-04-18 17:14:24','great game!!!');
INSERT INTO "replyText" VALUES(8,1,'2024-04-18 17:15:28','blue, green, yellow');
INSERT INTO "replyText" VALUES(9,1,'2024-04-18 17:57:45','hey');
INSERT INTO "replyText" VALUES(10,1,'2024-04-18 18:10:34','it is fun indeed');
INSERT INTO "replyText" VALUES(11,1,'2024-04-19 00:10:53','solitare is a nice game');
INSERT INTO "replyText" VALUES(12,24,'2024-04-19 00:23:53','yeah I love it too');
INSERT INTO "replyText" VALUES(13,30,'2024-04-19 00:24:16','omg it was a classic!!!');
INSERT INTO "replyText" VALUES(14,33,'2024-04-19 22:42:05','I disagree I think COPA AMERICA is better');
INSERT INTO "replyText" VALUES(15,1,'2024-04-19 22:43:25','maan shut up');
INSERT INTO "replyText" VALUES(16,1,'2024-04-20 12:16:25','I agree');
INSERT INTO "replyText" VALUES(17,1,'2024-04-20 12:33:18','I agree');
INSERT INTO "replyText" VALUES(18,1,'2024-04-21 13:49:58','yo');
INSERT INTO "replyText" VALUES(19,1,'2024-04-21 13:56:59','jsqjgsq');
INSERT INTO "replyText" VALUES(20,1,'2024-04-21 14:16:38','dwhdhwaiu');
INSERT INTO "replyText" VALUES(21,1,'2024-04-21 14:21:32','awdawd');
INSERT INTO "replyText" VALUES(22,1,'2024-04-21 14:48:22','awd');
INSERT INTO "replyText" VALUES(23,1,'2024-04-21 15:24:09','awd');
INSERT INTO "replyText" VALUES(24,1,'2024-04-21 15:24:47','This is a test');
INSERT INTO "replyText" VALUES(25,1,'2024-04-21 15:44:07','test');
INSERT INTO "replyText" VALUES(26,1,'2024-04-22 16:46:25','Indeed it does it is a great way to increase the brain capacity');
INSERT INTO "replyText" VALUES(27,31,'2024-04-22 16:47:18','yes it is true');
INSERT INTO "replyText" VALUES(28,1,'2024-04-23 13:24:57','hey');
INSERT INTO "replyText" VALUES(29,1,'2024-04-23 13:31:25','heyyo');
INSERT INTO "replyText" VALUES(30,1,'2024-04-23 13:31:56','heyyyyy');
INSERT INTO "replyText" VALUES(31,1,'2024-04-23 13:35:45','test 1234');
INSERT INTO "replyText" VALUES(32,1,'2024-04-23 13:36:33','test 56789');
INSERT INTO "replyText" VALUES(33,1,'2024-04-23 13:42:22','is this working ?');
INSERT INTO "replyText" VALUES(34,1,'2024-04-23 13:47:35','please work!');
INSERT INTO "replyText" VALUES(35,1,'2024-04-23 13:49:47','test again!');
INSERT INTO "replyText" VALUES(36,1,'2024-04-23 13:53:04','please work');
INSERT INTO "replyText" VALUES(37,1,'2024-04-23 13:55:58','will the reply stay after refresh ?');
INSERT INTO "replyText" VALUES(38,1,'2024-04-23 13:57:07','please stay!');
INSERT INTO "replyText" VALUES(39,1,'2024-04-23 14:09:03','is it working?');
INSERT INTO "replyText" VALUES(40,1,'2024-04-23 14:14:45','hey');
INSERT INTO "replyText" VALUES(41,1,'2024-04-23 14:19:57','yes');
INSERT INTO "replyText" VALUES(42,1,'2024-04-23 14:20:25','me too');
INSERT INTO "replyText" VALUES(43,33,'2024-04-23 21:21:15','why would you say that unless you have proof to show here');
INSERT INTO "replyText" VALUES(44,33,'2024-04-23 21:21:46','test 1');
INSERT INTO "replyText" VALUES(45,2,'2024-04-23 21:23:34','I do agree with him he is stating facts!');
INSERT INTO "replyText" VALUES(46,1,'2024-04-23 21:23:49','is he though ?');
INSERT INTO "replyText" VALUES(47,1,'2024-04-28 17:08:26','surely not');
INSERT INTO "replyText" VALUES(48,1,'2024-04-28 17:17:09','hey');
INSERT INTO "replyText" VALUES(49,1,'2024-04-28 17:22:26','hey');
INSERT INTO "replyText" VALUES(50,1,'2024-04-28 18:27:23','It is a classic game for sure');
CREATE TABLE replyToClaim (
    replyToClaimID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,                                       -- Relationship ID
    reply INTEGER NOT NULL REFERENCES replyText (replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,   -- FK of related reply
    claim INTEGER NOT NULL REFERENCES claim (claimID) ON DELETE CASCADE ON UPDATE CASCADE,           -- FK of related claim
    replyToClaimRelType INTEGER NOT NULL REFERENCES replyToClaimType(claimReplyTypeID) ON DELETE CASCADE ON UPDATE CASCADE -- FK of relation type
);
INSERT INTO "replyToClaim" VALUES(1,1,6,1);
INSERT INTO "replyToClaim" VALUES(2,2,6,1);
INSERT INTO "replyToClaim" VALUES(3,3,6,1);
INSERT INTO "replyToClaim" VALUES(4,4,6,1);
INSERT INTO "replyToClaim" VALUES(5,5,6,1);
INSERT INTO "replyToClaim" VALUES(6,6,6,1);
INSERT INTO "replyToClaim" VALUES(7,7,6,1);
INSERT INTO "replyToClaim" VALUES(8,8,5,1);
INSERT INTO "replyToClaim" VALUES(9,9,6,1);
INSERT INTO "replyToClaim" VALUES(10,10,4,1);
INSERT INTO "replyToClaim" VALUES(11,11,7,1);
INSERT INTO "replyToClaim" VALUES(12,12,7,1);
INSERT INTO "replyToClaim" VALUES(13,13,7,1);
INSERT INTO "replyToClaim" VALUES(14,14,8,1);
INSERT INTO "replyToClaim" VALUES(15,15,8,1);
INSERT INTO "replyToClaim" VALUES(16,16,9,1);
INSERT INTO "replyToClaim" VALUES(17,17,10,1);
INSERT INTO "replyToClaim" VALUES(18,18,11,1);
INSERT INTO "replyToClaim" VALUES(19,19,11,1);
INSERT INTO "replyToClaim" VALUES(20,20,11,1);
INSERT INTO "replyToClaim" VALUES(21,21,18,1);
INSERT INTO "replyToClaim" VALUES(22,22,20,1);
INSERT INTO "replyToClaim" VALUES(23,23,20,1);
INSERT INTO "replyToClaim" VALUES(24,24,20,1);
INSERT INTO "replyToClaim" VALUES(25,25,20,1);
INSERT INTO "replyToClaim" VALUES(26,26,14,1);
INSERT INTO "replyToClaim" VALUES(27,27,26,1);
INSERT INTO "replyToClaim" VALUES(28,43,15,1);
INSERT INTO "replyToClaim" VALUES(29,45,15,1);
INSERT INTO "replyToClaim" VALUES(30,50,7,1);
CREATE TABLE replyToClaimType (
    claimReplyTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    claimReplyType TEXT NOT NULL
);
INSERT INTO "replyToClaimType" VALUES(1,'Clarification');
INSERT INTO "replyToClaimType" VALUES(2,'Supporting Argument');
INSERT INTO "replyToClaimType" VALUES(3,'Counterargument');
CREATE TABLE replyToReply (
    replyToReplyID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,                                         -- Relationship ID
    reply INTEGER NOT NULL REFERENCES replyText(replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,
    parent INTEGER NOT NULL REFERENCES replyText(replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,
    replyToReplyRelType INTEGER NOT NULL REFERENCES replyToReplyType(replyReplyTypeID) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "replyToReply" VALUES(1,'test',20,1);
INSERT INTO "replyToReply" VALUES(31,'yes it is true',26,1);
INSERT INTO "replyToReply" VALUES(32,28,26,1);
INSERT INTO "replyToReply" VALUES(33,29,26,1);
INSERT INTO "replyToReply" VALUES(34,30,26,1);
INSERT INTO "replyToReply" VALUES(35,31,26,1);
INSERT INTO "replyToReply" VALUES(36,32,26,1);
INSERT INTO "replyToReply" VALUES(37,33,26,1);
INSERT INTO "replyToReply" VALUES(38,34,26,1);
INSERT INTO "replyToReply" VALUES(39,35,26,1);
INSERT INTO "replyToReply" VALUES(40,36,26,1);
INSERT INTO "replyToReply" VALUES(41,37,26,1);
INSERT INTO "replyToReply" VALUES(42,38,26,1);
INSERT INTO "replyToReply" VALUES(43,39,26,1);
INSERT INTO "replyToReply" VALUES(44,40,26,1);
INSERT INTO "replyToReply" VALUES(45,41,26,1);
INSERT INTO "replyToReply" VALUES(46,42,16,1);
INSERT INTO "replyToReply" VALUES(47,44,43,1);
INSERT INTO "replyToReply" VALUES(48,46,45,1);
INSERT INTO "replyToReply" VALUES(49,47,45,1);
INSERT INTO "replyToReply" VALUES(50,48,45,1);
INSERT INTO "replyToReply" VALUES(51,49,45,1);
CREATE TABLE replyToReplyType (
    replyReplyTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    replyReplyType TEXT NOT NULL
);
INSERT INTO "replyToReplyType" VALUES(1,'Evidence');
INSERT INTO "replyToReplyType" VALUES(2,'Support');
INSERT INTO "replyToReplyType" VALUES(3,'Rebuttal');
CREATE TABLE topic (
    topicID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,  -- Topic's ID number
    topicName TEXT NOT NULL,                             -- Topic's text
    postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE, -- FK (foreign key) of posting user
    creationTime INTEGER NOT NULL,                       -- Time topic was created
    updateTime INTEGER NOT NULL                          -- Last time a claim/reply was added
);
INSERT INTO "topic" VALUES(1,'galatasaray','zeki','2024-04-17 16:17:57','2024-04-17 16:17:57');
INSERT INTO "topic" VALUES(2,'test','zeki','2024-04-17 17:21:17','2024-04-17 17:21:17');
INSERT INTO "topic" VALUES(3,'Rainbow','zeki','2024-04-17 17:57:33','2024-04-17 17:57:33');
INSERT INTO "topic" VALUES(4,'PC Games','zeki','2024-04-18 00:48:54','2024-04-18 00:48:54');
INSERT INTO "topic" VALUES(5,'Champions League','x31canavari69x','2024-04-19 23:41:03','2024-04-19 23:41:03');
INSERT INTO "topic" VALUES(6,'Oxford Brookes Uni','zeki','2024-04-20 13:32:15','2024-04-20 13:32:15');
INSERT INTO "topic" VALUES(7,'Reading helps brain development','selinn','2024-04-22 17:44:14','2024-04-22 17:44:14');
CREATE TABLE user (
    userID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- Integer user ID / key
    userName TEXT NOT NULL,                            -- Login username
    passwordHash BLOB NOT NULL,                        -- Hashed password (bytes in python)
    isAdmin BOOLEAN NOT NULL,                          -- If user is admin or not. Ignore if not implementing admin
    creationTime INTEGER NOT NULL,                     -- Time user was created
    lastVisit INTEGER NOT NULL                         -- User's last visit, for showing new content when they return
);
INSERT INTO "user" VALUES(1,'zeki','sarak',0,'2024-04-16 01:49:41','2024-04-16 01:49:41');
INSERT INTO "user" VALUES(2,'can','sarak',0,'2024-04-16 02:43:44','2024-04-16 02:43:44');
INSERT INTO "user" VALUES(3,'gokhan','190519051905',0,'2024-04-16 02:46:19','2024-04-16 02:46:19');
INSERT INTO "user" VALUES(4,'cem','sarak',0,'2024-04-16 03:22:24','2024-04-16 03:22:24');
INSERT INTO "user" VALUES(5,'birsen','birsen',0,'2024-04-16 03:23:46','2024-04-16 03:23:46');
INSERT INTO "user" VALUES(6,'emre','sarak',0,'2024-04-16 03:27:25','2024-04-16 03:27:25');
INSERT INTO "user" VALUES(7,'Atakan','sarak',0,'2024-04-16 03:29:18','2024-04-16 03:29:18');
INSERT INTO "user" VALUES(8,'cansarak','sarak',0,'2024-04-16 03:31:19','2024-04-16 03:31:19');
INSERT INTO "user" VALUES(9,'cansarak','sarak',0,'2024-04-16 03:31:19','2024-04-16 03:31:19');
INSERT INTO "user" VALUES(10,'cancan','sarak',0,'2024-04-16 03:37:20','2024-04-16 03:37:20');
INSERT INTO "user" VALUES(11,'cancan','sarak',0,'2024-04-16 03:37:20','2024-04-16 03:37:20');
INSERT INTO "user" VALUES(12,'cancancan','sarak',0,'2024-04-16 03:38:57','2024-04-16 03:38:57');
INSERT INTO "user" VALUES(13,'cancancan','sarak',0,'2024-04-16 03:38:57','2024-04-16 03:38:57');
INSERT INTO "user" VALUES(14,'saraklar','sarak',0,'2024-04-16 03:40:29','2024-04-16 03:40:29');
INSERT INTO "user" VALUES(15,'saraklar','sarak',0,'2024-04-16 03:40:29','2024-04-16 03:40:29');
INSERT INTO "user" VALUES(16,'emrecik','sarak',0,'2024-04-16 03:42:33','2024-04-16 03:42:33');
INSERT INTO "user" VALUES(17,'emrecik','sarak',0,'2024-04-16 03:42:33','2024-04-16 03:42:33');
INSERT INTO "user" VALUES(18,'selin','sarak',0,'2024-04-16 04:11:08','2024-04-16 04:11:08');
INSERT INTO "user" VALUES(19,'cansarak2002','sarak',0,'2024-04-16 04:18:16','2024-04-16 04:18:16');
INSERT INTO "user" VALUES(20,'selo','sarak',0,'2024-04-16 04:21:22','2024-04-16 04:21:22');
INSERT INTO "user" VALUES(21,'zekicansarak','sarak',0,'2024-04-16 04:28:21','2024-04-16 04:28:21');
INSERT INTO "user" VALUES(22,'abuzer','sarak',0,'2024-04-16 04:35:21','2024-04-16 04:35:21');
INSERT INTO "user" VALUES(23,'zekiiiii','sarak',0,'2024-04-16 04:51:36','2024-04-16 04:51:36');
INSERT INTO "user" VALUES(24,'selinn','sarak',0,'2024-04-16 04:54:48','2024-04-16 04:54:48');
INSERT INTO "user" VALUES(25,'hey','sarak',0,'2024-04-16 05:05:35','2024-04-16 05:05:35');
INSERT INTO "user" VALUES(26,'ha','sarak',0,'2024-04-16 19:44:11','2024-04-16 19:44:11');
INSERT INTO "user" VALUES(27,'nilsu','sarak',0,'2024-04-16 19:55:39','2024-04-16 19:55:39');
INSERT INTO "user" VALUES(28,'Emreyy','sarak',0,'2024-04-16 20:04:41','2024-04-16 20:04:41');
INSERT INTO "user" VALUES(29,'zcansarak','sarak',0,'2024-04-18 00:10:04','2024-04-18 00:10:04');
INSERT INTO "user" VALUES(30,'benim','sarak',0,'2024-04-18 00:41:18.877666','2024-04-18 00:41:18.877666');
INSERT INTO "user" VALUES(31,'huso','sarak',0,'2024-04-18 00:46:32.883995','2024-04-18 00:46:32.883995');
INSERT INTO "user" VALUES(32,'melto','sarak',0,'2024-04-18 00:47:57.115769','2024-04-18 00:47:57.115769');
INSERT INTO "user" VALUES(33,'x31canavari69x','ahmet',0,'2024-04-19 23:40:26.166038','2024-04-19 23:40:26.166038');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('claimToClaimType',2);
INSERT INTO "sqlite_sequence" VALUES('replyToClaimType',3);
INSERT INTO "sqlite_sequence" VALUES('replyToReplyType',3);
INSERT INTO "sqlite_sequence" VALUES('user',33);
INSERT INTO "sqlite_sequence" VALUES('topic',7);
INSERT INTO "sqlite_sequence" VALUES('claim',16);
INSERT INTO "sqlite_sequence" VALUES('replyText',50);
INSERT INTO "sqlite_sequence" VALUES('replyToClaim',30);
INSERT INTO "sqlite_sequence" VALUES('replyToReply',51);
INSERT INTO "sqlite_sequence" VALUES('claimToClaim',2);
COMMIT;
