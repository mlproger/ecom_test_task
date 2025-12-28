-- Миграция: создаёт нормализованные таблицы для студентов и оценок
-- Запуск: psql $DATABASE_URL -f migrations/create_tables.sql

BEGIN;

-- Таблица студентов: уникальное ФИО и опционально номер группы
CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL UNIQUE,
  group_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Таблица оценок: связь с students, дата оценки, предмет (опционально), значение 1..5
CREATE TABLE IF NOT EXISTS grades (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  grade SMALLINT NOT NULL CHECK (grade BETWEEN 1 AND 5),
  grade_date DATE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Индексы для ускорения аналитических запросов
CREATE INDEX IF NOT EXISTS idx_grades_student_id ON grades(student_id);
CREATE INDEX IF NOT EXISTS idx_grades_grade_date ON grades(grade_date);
CREATE INDEX IF NOT EXISTS idx_students_group_name ON students(group_name);

-- Частичный индекс для быстрого подсчёта двоек по студенту
CREATE INDEX IF NOT EXISTS idx_grades_student_twos ON grades(student_id) WHERE grade = 2;

COMMIT;

-- Create students and grades tables
CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS grades (
  id SERIAL PRIMARY KEY,
  student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  grade INT NOT NULL CHECK (grade >= 1 AND grade <= 5),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS grades_student_idx ON grades(student_id);
CREATE INDEX IF NOT EXISTS grades_grade_idx ON grades(grade);
