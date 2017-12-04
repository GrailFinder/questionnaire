import json
from services.questmaker.tests.base import BaseTestCase
from utils import add_quest, add_answer

class TestAnswerService(BaseTestCase):
    """Tests for the Answers"""

    def test_add_answer(self):
        """Ensure that creating new answer behaves normal"""
        with self.client:
            response = self.client.post(
                "/answer",
                data=json.dumps(dict(
                    text="testone"
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])


    def test_single_quest(self):
        """test getting answer by id"""

        answ = add_answer(text="Are you even test?")
        with self.client:
            response = self.client.get(f'quest/{answ.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('Are you even test?', data['data']['text'])
            self.assertIn('success', data['status'])