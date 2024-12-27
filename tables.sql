DROP TABLE searches;
DROP TABLE clients;
DROP TABLE files;
DROP TABLE sequences;
DROP TABLE samples;
DROP TABLE sqlite_sequence;

CREATE TABLE searches(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    user_id INTEGER NOT NULL,    
    file_id INTEGER NOT NULL,
    FOREIGN KEY(file_id) REFERENCES files(id),
    FOREIGN KEY(user_id) REFERENCES clients(id)
);


PRAGMA foreign_keys = ON;

CREATE TABLE clients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE files(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name Varchar(50) NOT NULL,
    file_data BLOB NOT NULL,
    title TEXT NOT NULL,
    history_image BLOB,
    num INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES clients(id)
);

CREATE TABLE sequences(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    words INTEGER,
    letters INTEGER,
    sentences INTEGER,
    syllables INTEGER,
    complex_words INTEGER,
    liau_index INTEGER,
    liau_age varchar(50),
    liau_grade varchar(50),
    flesch_kincaid_index INTEGER,
    flesch_kincaid_grade varchar(50),
    gunning_fog_index INTEGER,
    gunning_fog_grade varchar(50),
    automated_readability_index INTEGER,
    automated_readability_grade varchar(50),    
    recommended_level varchar(50),
    file_id INTEGER NOT NULL,
    FOREIGN KEY(file_id) REFERENCES files(id)
);

CREATE TABLE samples(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    names varchar(50),
    words INTEGER,
    letters INTEGER,
    sentences INTEGER,
    syllables INTEGER,
    complex_words INTEGER,
    liau_index INTEGER,
    liau_age varchar(50),
    liau_grade varchar(50),
    flesch_kincaid_index INTEGER,
    flesch_kincaid_grade varchar(50),
    gunning_fog_index INTEGER,
    gunning_fog_grade varchar(50),
    automated_readability_index INTEGER,
    automated_readability_grade varchar(50),  
    recommended_level varchar(50)  
);

INSERT INTO samples (names, words,letters,sentences,syllables,complex_words,liau_index,liau_age,liau_grade, flesch_kincaid_index,flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level) VALUES ("Animal Farm", 30280, 133646, 1691, 44903, 3805, 10, "<7", "Grade 0", 63, "8th & 9th Grade", 12, "High School Senior", 8, "8th Grade", "8");
INSERT INTO samples (names, words,letters,sentences,syllables,complex_words,liau_index,liau_age,liau_grade, flesch_kincaid_index,flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level) VALUES ("Of Mice and Men", 30058, 117343, 3615, 39512, 1327, 10, "~13-14", "7th Grade", 87, "6th Grade", 5, "5th Grade", 1, "Kindergarden", "6");
INSERT INTO samples (names, words,letters,sentences,syllables,complex_words,liau_index,liau_age,liau_grade, flesch_kincaid_index,flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level) VALUES ("A Doll's House", 26980, 97552, 6289, 33196, 1413, 5, "~11-12", "5th Grade", 98, "5th Grade", 4, "4th Grade", -2, "Pre-KG", "5");
INSERT INTO samples (names, words,letters,sentences,syllables,complex_words,liau_index,liau_age,liau_grade, flesch_kincaid_index,flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level) VALUES ("The Great Gatsby", 49514, 206267, 3646, 71605, 5219, 9, "~15-16", "9th Grade", 71, "7th Grade", 10, "High School Sophmore", 5, "5th Grade", "8");
INSERT INTO samples (names, words,letters,sentences,syllables,complex_words,liau_index,liau_age,liau_grade, flesch_kincaid_index,flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level) VALUES ("Things Fall Apart", 54185, 225427, 4047, 75786, 4525, 9, "~15-16", "9th Grade", 75, "7th Grade", 9, "High School Freshman", 5, "5th Grade", "8");
INSERT INTO samples (names, words,letters,sentences,syllables,complex_words,liau_index,liau_age,liau_grade, flesch_kincaid_index,flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level) VALUES ("Harry Potter and the Order of the Phoenix", 275962, 1163882, 25755, 397678, 27426, 9, "~15-16", "9th Grade", 74, "7th Grade", 8, "8th Grade", 4, "4th Grade", "7");
INSERT INTO samples (names, words,letters,sentences,syllables,complex_words,liau_index,liau_age,liau_grade, flesch_kincaid_index,flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level) VALUES ("Lord of the Flies", 67003, 271712, 6038, 89147, 4849, 8, "~14-15", "8th Grade", 83, "6th Grade", 7, "7th Grade", 3, "3rd Grade", "6");