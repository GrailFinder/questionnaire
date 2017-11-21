import json
from services.questmaker.tests.base import BaseTestCase


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
            response = self.client.post(
                "/quest",
                data=json.dumps(dict(
                    title="Can you read?"
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])