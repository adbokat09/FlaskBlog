DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS post_tags;
DROP TABLE IF EXISTS tags;


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  short_description TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE likes (
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    like_status BOOLEAN,
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES post (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE tags (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES post (id),
    FOREIGN KEY (tag_id) REFERENCES tags (id)
);

