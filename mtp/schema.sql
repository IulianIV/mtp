DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS budget_expense;
DROP TABLE IF EXISTS budget_revenue;
DROP TABLE IF EXISTS budget_savings;
DROP TABLE IF EXISTS budget_utilities;
DROP TABLE IF EXISTS collections_ledger;
DROP TABLE IF EXISTS collections_media;
DROP TABLE IF EXISTS health_biometrics;
DROP TABLE IF EXISTS health_workout;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEST NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);



validation_tables = ['types', 'levels', 'regions', 'workouts', 'reps', 'sets']

types = ['body weight', 'weighted']
levels = ['beginner', 'intermediate', 'advanced']
regions = ['Anterior Lower - Squats', 'Upper Push', 'Posterior Lower - Hinge', 'Upper Pull', 'Abs', 'Corrective',
           'Anterior Lower - Lunge', 'Calf', 'Forearm', 'Postural', 'Stretch']
workouts = ['Workout A', 'Workout B', 'Variation A', 'Variation B', 'Variation C', 'Rest day']
reps = ['8-12']
sets = ['3', '1 minute', '45 seconds', 'failure']
