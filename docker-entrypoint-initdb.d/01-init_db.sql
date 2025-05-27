CREATE TABLE source (
       s_id INTEGER NOT NULL PRIMARY KEY,
       s_name TEXT,
       s_comment TEXT
);
CREATE TABLE target (
       t_id INTEGER NOT NULL PRIMARY KEY,
       t_name TEXT,
       t_comment TEXT
);
CREATE TABLE relation (
       id SERIAL PRIMARY KEY,
       r_s_id INTEGER,
       r_t_id INTEGER
);
ALTER TABLE relation
      ADD CONSTRAINT fk_r_s FOREIGN KEY (r_s_id)
      REFERENCES source (s_id);
ALTER TABLE relation
      ADD CONSTRAINT fk_r_t FOREIGN KEY (r_t_id)
      REFERENCES target (t_id);

INSERT INTO source (s_id, s_name, s_comment)
VALUES
(1, 'first', 'my first source'),
(2, 'second', 'my second source'),
(3, 'third', 'my third source'),
(4, 'fourth', 'my fourth source')
;

INSERT INTO target (t_id, t_name, t_comment)
VALUES
(1, 'A', 'Target A'),
(2, 'B', 'Target B'),
(3, 'C', 'Target C'),
(4, 'D', 'Target D')
;

INSERT INTO relation (r_s_id, r_t_id)
VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 4),
(3, 4),
(4, 4)
;
