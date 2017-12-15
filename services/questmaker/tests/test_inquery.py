import json
from services.questmaker.tests.base import BaseTestCase
from utils import add_quest, add_inquiry

class TestinquiryService(BaseTestCase):
    """Tests for the inquiries"""

    def test_add_inquiry(self):
        """Ensure that creating new inquiry behaves normal"""
        with self.client:
            response = self.client.post(
                "/inquiries",
                data=json.dumps(dict(
                    title="testone"
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])


    def test_single_inquiry(self):
        """test getting inquiry by id"""

        inq = add_inquiry(title="Are you even test?")
        with self.client:
            response = self.client.get(f'inquiry/{inq.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('Are you even test?', data['data']['title'])
            self.assertIn('success', data['status'])