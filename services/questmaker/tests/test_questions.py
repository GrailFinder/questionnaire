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