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
        self.database_path = 'postgresql://postgres:1234@localhost:5432/trivia'
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    # questions

    def test_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['currentCategory'], None)
        self.assertTrue(data['categories'])

    # delete questions

    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(question, None)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_question_not_found(self):
        res = self.client().delete('/questions/1200')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])
        self.assertIsNotNone(data['message'])
        self.assertEqual(data['message'], 'resource not found')

    # add question

    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # search question

    def test_search_question_with_results(self):
        res = self.client().post('/questions/search',
                                    json={'searchTerm': 'fantasy'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['currentCategory'], None)

    def test_search_question_without_results(self):
        res = self.client().post('/questions/search',
                                    json={'searchTerm': 'susuki'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], [])
        self.assertEqual(data['totalQuestions'], 0)
        self.assertEqual(data['currentCategory'], None)

    # get questions by category

    def test_questions_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])
        self.assertTrue(data['categories'])
        res = self.client().get('/categories')

    def test_404_questions_category(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])
        self.assertIsNotNone(data['message'])
        self.assertEqual(data['message'], 'resource not found')

    # play quizze

    def test_play_all_categories(self):
        res = self.client().post('/play',
                                    json={'previous_questions': [], 'quiz_category': {'type': "all", 'id': 0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # test other categories

    def test_play_category(self):
        res = self.client().post('/play',
                                    json={'previous_questions': [5, 7], 'quiz_category': {'type': "Science", 'id': 1}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_play_failed(self):
        res = self.client().post('/play',
                                    json={'previous_questions': [5, 7], 'quiz_category': {'type': "all", 'id': 1200}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])
        self.assertIsNotNone(data['message'])
        self.assertEqual(data['message'], 'resource not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()