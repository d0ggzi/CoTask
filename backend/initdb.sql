CREATE TABLE IF NOT EXISTS teams
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS users
(
    id       SERIAL PRIMARY KEY,
    email VARCHAR(50) NOT NULL UNIQUE,
    password TEXT        NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    position VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dashboards
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS team_dashboards
(
    team_id   INT NOT NULL,
    dash_id   INT NOT NULL,
    CONSTRAINT fk_team_dash_id
        FOREIGN KEY (team_id)
            REFERENCES teams (id),
    CONSTRAINT fk_dash_team_id
        FOREIGN KEY (dash_id)
            REFERENCES dashboards (id)
);

CREATE TYPE status AS ENUM ('backlog', 'todo', 'process', 'finished');


CREATE TABLE IF NOT EXISTS tasks
(
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL,
    current_status status,
    complete_percent int,
    description TEXT,
    start_date timestamp,
    end_date timestamp,
    fact_end_date timestamp,
    duration float
);

CREATE TABLE IF NOT EXISTS task_to_task
(
    first_task_id   INT NOT NULL,
    second_task_id   INT NOT NULL,
    CONSTRAINT fk_first_task_id
        FOREIGN KEY (first_task_id)
            REFERENCES tasks (id),
    CONSTRAINT fk_second_task_id
        FOREIGN KEY (second_task_id)
            REFERENCES tasks (id)
);

CREATE TABLE IF NOT EXISTS user_task
(
    user_id   INT NOT NULL,
    task_id   INT NOT NULL,
    CONSTRAINT fk_user_id
        FOREIGN KEY (user_id)
            REFERENCES users (id),
    CONSTRAINT fk_task_id
        FOREIGN KEY (task_id)
            REFERENCES tasks (id)
);

CREATE TABLE IF NOT EXISTS task_dashboards
(
    task_id   INT NOT NULL,
    dash_id   INT NOT NULL,
    CONSTRAINT fk_task_id
        FOREIGN KEY (task_id)
            REFERENCES tasks (id),
    CONSTRAINT fk_dash_id
        FOREIGN KEY (dash_id)
            REFERENCES dashboards (id)
);

CREATE TABLE IF NOT EXISTS user_team
(
    team_id   INT NOT NULL,
    user_id   INT NOT NULL,
    CONSTRAINT fk_team_id
        FOREIGN KEY (team_id)
            REFERENCES teams (id),
    CONSTRAINT fk_user_id
        FOREIGN KEY (user_id)
            REFERENCES users (id)
);


CREATE TABLE IF NOT EXISTS task_team
(
    task_id   INT NOT NULL,
    team_id   INT NOT NULL,
    CONSTRAINT fk_task_id
        FOREIGN KEY (task_id)
            REFERENCES tasks (id),
    CONSTRAINT fk_team_id
        FOREIGN KEY (team_id)
            REFERENCES teams (id)
);


-- INSERT INTO teams
-- VALUES (1, 'developer'),
--        (2, 'designer'),
--        (3, 'project manager')
-- ON CONFLICT DO NOTHING;
INSERT INTO users (email, password, fullname, position)
VALUES ('admin@admin.com', '$2b$12$EHBjw4WFX4p/BtiYoYMWQ.2wnS/9cnN/KCJPjXm1gAXGjq88BHkWK', 'Admin Adminovich', 'Admin')
ON CONFLICT DO NOTHING;

-- password admin