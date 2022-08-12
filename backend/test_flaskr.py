import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from config import SQLALCHEMY_DATABASE_URI


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"

        database_name = 'trivia'
        database_password = 'postgres'
        database_user = 'postgres'
        database_host = 'localhost:5432'
        self.database_path = SQLALCHEMY_DATABASE_URI

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # ====================================================================================
    # Tests for /categories
    # ====================================================================================
    # successful operation
    def test_get_all_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_error_get_all_categories(self):
        res = self.client().get("/categorie")
        data = json.loads(res.data)
        # print("\n Categories error: ", data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # ====================================================================================
    # Tests for /questions?page=${integer}
    # ====================================================================================
    # successful operation

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        # confirm the presence od all necessary keys and their values
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['currentCategory'])

        # confirm that total number of questions are valid
        self.assertEqual(len(data['questions']), data['totalQuestions'])

    # requesting beyond valid page number

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

 # ====================================================================================
    # Tests for /questions?page=${integer}
    # ====================================================================================
    # successful operation

    def test_get_paginated_questions_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        # confirm the presence od all necessary keys and their values
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['currentCategory'], 'Art')

        # confirm that total number of questions are valid
        self.assertEqual(len(data['questions']), data['totalQuestions'])

    # requesting beyond valid category id
    def test_404_sent_requesting_beyond_valid_categories(self):
        # To be sure the category does not exist
        category_id = Category.query.count() + 10
        res = self.client().get("/categories/{}/questions".format(category_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # ====================================================================================
    # post a new question
    # Tests for /questions method = ['POST']
    # ====================================================================================
    # successful operation

    def test_add_a_new_question(self):
        testQuestion = {
            'question':  'Test Heres a another new question string',
            'answer':  'Heres the new answer string',
            'difficulty': 5,
            'category': 2
        }

        res = self.client().post('/questions', json=testQuestion)

        question = Question.query.filter(
            Question.question == testQuestion['question']).one_or_none()

        data = json.loads(res.data)
        # print("\n\nadd new question: ", data, '\n\n')
        self.assertTrue(data['success'], True)
        # self.assertEqual(question["question"], testQuestion['question'])
        # self.assertEqual(question["answer"], testQuestion['answer'])
        # self.assertEqual(question["difficulty"], testQuestion['difficulty'])
        # self.assertEqual(question["category"], testQuestion['category'])

    # test 422_body incomplete (body has no question)
    def test_422_adding_question_without_a_required_field(self):
        testQuestion = {
            'answer':  'testing for wrong answer',
            'difficulty': 1,
            'category': 3,
        }

        res = self.client().post('/questions', json=testQuestion)
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.answer == testQuestion['answer']).one_or_none()
        self.assertIsNone(question)
        self.assertTrue(res.status_code, 422)
    # ====================================================================================
    # Delete a question
    # Tests for /questions/{id} method = ['DELETE']
    # ====================================================================================
    # successful operation

    def test_delete_question(self):
        # I brought the delete below the insert test so it will delete the data that the
        # insert put into the database
        question = Question.query.with_entities(
            Question.id).order_by(Question.id.desc()).first()
        question_id = question.id
        # print("Question id", question_id)
        res = self.client().delete('/questions/{}'.format(question_id))
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertEqual(data['id'], question_id)

        self.assertEqual(question, None)

    # # unsuccessful operation
    def test_422_if_question_does_not_exit(self):
        # To be sure the questions not exist
        question_id = Question.query.count() + 100
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # ====================================================================================
    # search
    # Tests for /questions method = ['POST']
    # ====================================================================================
    # successful operation
    def test_search(self):
        res = self.client().post("/questions", json={"searchTerm": "ancient"})

        data = json.loads(res.data)
        # print("\nancient: ", data, "\n")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['currentCategory'])

    # # unsuccessful operation
    def test_search_empty_results(self):
        res = self.client().post("/questions",
                                 json={"searchTerm": "cbaucvvbvue;89764777736375quvevccquecbecue785387e5127e128e1e7521e"})
        data = json.loads(res.data)
        # print("search: ", data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # ====================================================================================
    # get questions to play
    # Tests for /quizzes method = ['POST']
    # ====================================================================================
    # successful test
    def test_quizzes(self):
        sendData = {
            'previous_questions': [1, 4, 20, 15],
            'quiz_category': {
                'type': 'Arts',
                'id': 1
            }
        }
        res = self.client().post("/quizzes", json=sendData)

        data = json.loads(res.data)
        # print("res: ", data, "\n\n\n")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['question'])

    # successful test
    def test_400_missing_request_data_quizzes(self):
        sendData = {
            'quiz_category': {
                'type': 'Arts',
                'id': 1
            }
        }
        res = self.client().post("/quizzes", json=sendData)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)


if __name__ == "__main__":
    unittest.main()
