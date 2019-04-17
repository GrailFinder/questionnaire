import json
from services.questmaker.tests.base import BaseTestCase
from services.questmaker.tests.utils import add_quest, add_choice

class TestChoiceService(BaseTestCase):
    """Tests for the Choices"""

    def test_add_choice(self):
        """Ensure that creating new choice behaves normal"""

        q = add_quest("do you love snow?")

        with self.client:
            response = self.client.post(
                "/choice",
                data=json.dumps(dict(
                    text="testone",
                    question_id=q.id,
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])


    def test_single_choice(self):
        """test getting choice by id"""

        q1 = add_quest("test?")

        choice = add_choice(text="Are you even test?", quest=q1)
        with self.client:
            response = self.client.get(f'choice/{choice.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('Are you even test?', data['data']['text'])
            self.assertIn('success', data['status'])