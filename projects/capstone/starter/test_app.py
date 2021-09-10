import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Gallery, Photo


class GalleryTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = 'postgresql://postgres:1234@localhost:5432/gallerytwo'
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # add gallery

    def test_add_question(self):
        res = self.client().post('/gallery/create')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        
    def test_get_galleries(self):
        res = self.client().get('/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['title'])

    # photos

    def test_photo(self):
        res = self.client().get('/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['photo_title'])

    # delete gallery

    def test_delete_gallery(self):
        res = self.client().delete('/gallery/1/delete')
        data = json.loads(res.data)

        gallery = Gallery.query.filter(Gallery.id == 1).one_or_none()

        self.assertEqual(gallery, None)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_question_not_found(self):
        res = self.client().delete('/gallery/1275/delete')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])
        self.assertIsNotNone(data['message'])
        self.assertEqual(data['message'], 'resource not found')

    def test_404_gallery(self):
        res = self.client().get('/1275')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])
        self.assertIsNotNone(data['message'])
        self.assertEqual(data['message'], 'resource not found')


    def test_success_Executive_get_all_galleries(self):
        for i in range(2):
            gallery = Gallery(title='gallery ' + str(i))
            gallery.insert()
        res = self.client().get('/')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_actors'], 2)
        self.assertTrue(len(data['actors']))

if __name__ == "__main__":
    unittest.main()
