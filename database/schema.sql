-- Smart Placement Preparation Assistant: schema + sample data
-- Run:  mysql -u root -p < database/schema.sql
CREATE DATABASE IF NOT EXISTS placement_assistant;
USE placement_assistant;

CREATE TABLE IF NOT EXISTS students (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL,
  branch     VARCHAR(60),
  study_year INT
);

CREATE TABLE IF NOT EXISTS questions (
  question_id     INT AUTO_INCREMENT PRIMARY KEY,
  title           VARCHAR(200) NOT NULL,
  category        VARCHAR(60)  NOT NULL,
  difficulty      VARCHAR(20)  DEFAULT 'Beginner',
  description     TEXT NOT NULL,
  sample_input    TEXT,
  expected_output TEXT
);

CREATE TABLE IF NOT EXISTS attempts (
  attempt_id       INT AUTO_INCREMENT PRIMARY KEY,
  student_id       INT NOT NULL,
  question_id      INT NOT NULL,
  submitted_answer TEXT,
  score            DECIMAL(5,2) DEFAULT 0,
  completed        BOOLEAN DEFAULT FALSE,
  attempted_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id)  REFERENCES students(student_id),
  FOREIGN KEY (question_id) REFERENCES questions(question_id)
);

-- Seeded demo student (the project has no login; see README limitations)
INSERT INTO students (full_name, branch, study_year) VALUES ('Demo Student', 'Computer Science Engineering', 3);

INSERT INTO questions (title, category, difficulty, description, sample_input, expected_output) VALUES
('Reverse a String', 'Strings', 'Beginner',
 'Write a Python function that takes a string and returns it reversed. Submit the output your solution prints for the sample input.',
 'hello', 'olleh'),
('Check Palindrome', 'Strings', 'Beginner',
 'A palindrome reads the same forwards and backwards. Write a function that prints True if the given word is a palindrome, otherwise False.',
 'madam', 'True'),
('Count Vowels', 'Strings', 'Beginner',
 'Count how many vowels (a, e, i, o, u) appear in the given word and print the count.',
 'placement', '3'),
('Find the Largest in a List', 'Lists', 'Beginner',
 'Given a list of integers, print the largest value without using the built-in max() function.',
 '[4, 9, 2, 7]', '9'),
('Remove Duplicates Preserving Order', 'Lists', 'Intermediate',
 'Remove duplicate values from a list while keeping the order of first appearance. Print the resulting list.',
 '[1, 2, 2, 3, 1, 4]', '[1, 2, 3, 4]'),
('Second Largest Element', 'Lists', 'Intermediate',
 'Print the second largest distinct number in the list. Try to solve it in a single pass.',
 '[10, 20, 4, 45, 99]', '45'),
('Word Frequency', 'Dictionaries', 'Intermediate',
 'Count how many times each word appears in a sentence and print the resulting dictionary (words in order of first appearance).',
 'to be or not to be', '{''to'': 2, ''be'': 2, ''or'': 1, ''not'': 1}'),
('Two Sum with a Dictionary', 'Dictionaries', 'Intermediate',
 'Given a list of numbers and a target, print the indices of the two numbers that add up to the target. Use a dictionary to do it in one pass.',
 'nums = [2, 7, 11, 15], target = 9', '[0, 1]'),
('Factorial Function', 'Functions', 'Beginner',
 'Write a function factorial(n) and print factorial(5). Try both a loop and a recursive version.',
 '5', '120'),
('First N Fibonacci Numbers', 'Functions', 'Intermediate',
 'Write a function that returns the first n Fibonacci numbers starting from 0. Print the list for the sample input.',
 '7', '[0, 1, 1, 2, 3, 5, 8]'),
('Prime Number Check', 'Numbers', 'Beginner',
 'Write a function that prints True if the number is prime, otherwise False. Hint: you only need to check divisors up to the square root.',
 '29', 'True'),
('Sum of Digits', 'Numbers', 'Beginner',
 'Print the sum of the digits of the given integer.',
 '4821', '15');
