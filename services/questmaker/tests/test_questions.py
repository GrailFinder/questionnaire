import json, uuid
from services.questmaker.tests.base import BaseTestCase
from services.questmaker.tests.utils import add_quest, add_user

class TestQuestionService(BaseTestCase):
    """Tests for the Questions Service."""

    def test_questions(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_question(self):
        """Ensure that creating new question behaves normal"""
        with self.client:

            user = add_user('test', 'test@test.com', 'test')
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )

            response = self.client.post(
                "/quest",
                data=json.dumps(dict(
                    title="Can you read?"
                )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])

    def test_get_all_questions(self):
        """Check get request for all questions"""
        response = self.client.get('/quest')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])


    def test_single_quest(self):
        """test getting question by id"""

        q = add_quest(title="Are you even test?")
        with self.client:
            response = self.client.get(f'quest/{q.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('Are you even test?', data['data']['title'])
            self.assertIn('success', data['status'])

    def test_edit_quest(self):
        """create and then edit test"""
        q = add_quest(title="Are you even test?")
        with self.client:
            # login
            user = add_user('test', 'test@test.com', 'test')
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            # edit quest
            resp = self.client.put(
                f"/question/{q.id}",
                data=json.dumps(dict(
                    title="Can you read?",
                    multichoice=False,
                )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
        # resp should contain status_code==204 only
        self.assertEqual(resp.status_code, 204)


    def test_create_question_by_put(self):
        """creates question using put"""
        random_id = uuid.uuid4()
        with self.client:
            # login
            user = add_user('test', 'test@test.com', 'test')
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            resp = self.client.put(
                f"/question/{random_id}",
                data=json.dumps(dict(
                    title="Can you read?",
                    multichoice=False,
                )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
                    )

