import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


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
        self.database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
            database_user, database_password, database_host, database_name)

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

    # ====================================================================================
    # Tests for /questions?page=${integer}
    # ====================================================================================
    # successful operation

    def test_get_paginated_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        # confirm the presence od all necessary keys and their values
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['currentCategory'])

        # confirm that total number of questions are valid
        totalLength = Question.query.count()
        self.assertEqual(len(data['totalQuestions']), totalLength)
        self.assertEqual(len(data['questions']), data['totalQuestions'])

    # requesting beyond valid page number

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'invalid page number requested')

    # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
