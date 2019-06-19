import json
from services.questmaker.tests.base import BaseTestCase
from services.questmaker.tests.utils import add_quest, add_inquiry, add_user, add_choice

class TestinquiryService(BaseTestCase):
    """Tests for the inquiries"""

    def test_add_inquiry(self):
        """Ensure that creating new inquiry behaves normal"""

        user = add_user('test', 'test@test.com', 'test')
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps(dict(
                email='test@test.com',
                password='test'
            )),
            content_type='application/json'
        )

        with self.client:
            response = self.client.post(
                "/inquiries",
                data=json.dumps(dict(
                    title="testone",
                    user_id=user.id,
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

    #TODO add anon inq creation test


    def test_single_inquiry(self):
        """test getting inquiry by id"""

        inq = add_inquiry(title="Are you even test?")
        with self.client:
            response = self.client.get(f'inq/{inq.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data)
            self.assertIn('Are you even test?', data['title'])

    def test_inq_view(self):
        """
        get all questions with all choices and other stuff
        {question: (multichoice, choice)}
        """
        # user
        u0 = add_user(username='grail', email="test@example.com", password='test')

        # first question
        i1 = add_inquiry(title="Who are you from the star wars?", user=u0)
        q1 = add_quest(title="How was your day, sweety?", inq=i1)
        a1 = add_choice("Okay", quest=q1)
        a2 = add_choice("Good", quest=q1)
        a3 = add_choice("Bad", quest=q1)
        a4 = add_choice("Who are you again?", quest=q1)

        q2 = add_quest(title="Anyway how is your sex life?", inq=i1)
        add_choice("You're just a little chicken", quest=q2)
        add_choice("Its not true, I did not hit her. I did not", quest=q2)
        add_choice("I am so happy to have you as my best friend and I love Lisa so much", quest=q2)
        add_choice("If a lot of people would love each other, the world would be a better place to live", quest=q2)


        with self.client:
            response = self.client.get(f'inq-view/{i1.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            print(data["data"])
            self.assertIn('How was your day, sweety?', data['data'])
            self.assertIn('success', data['status'])
            self.assertIn('Good', data['data']['How was your day, sweety?']["choice"].values())
            self.assertFalse(data['data']['How was your day, sweety?']["multichoice"])
