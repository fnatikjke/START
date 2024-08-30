CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'Qq12345';
SELECT pg_create_physical_replication_slot('replication_slot');

CREATE database arkh_test OWNER postgres;
\c arkh_test postgres;

CREATE TABLE Email (
  ID SERIAL PRIMARY KEY,
  "Электронная почта" VARCHAR(100) NOT NULL
);

CREATE TABLE Телефон (
  ID SERIAL PRIMARY KEY,
  "Номер телефона" VARCHAR(100) NOT NULL
);

INSERT INTO Email ("Электронная почта") VALUES
    ('pavel@ya.ru'),
    ('jane@example.com');

INSERT INTO Телефон ("Номер телефона") VALUES
    ('+79006789301'),
    ('+79163457384');
