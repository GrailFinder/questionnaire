import json
from services.questmaker.tests.base import BaseTestCase
from services.questmaker.tests.utils import add_quest, add_inquiry, add_user, add_choice, add_answer


class TestAnswerService(BaseTestCase):
    """
    answer tests
    """

    def test_answers_creation(self):
        inq = add_inquiry(title="Are you even test?")
        q = add_quest(title="Are you even question?", inq=inq)
        ch = add_choice(text="Are you even test?", quest=q)


        answ_fields = {
            #"id": fields.String,
            "inq_id": inq.id,
            "quest_id": q.id,
            "choice_id": ch.id,
        }


        with self.client:
            response = self.client.post(
                "/answers",
                # put answer in list
                data=json.dumps([answ_fields]),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])


    def test_answer_get(self):
        inq = add_inquiry(title="Are you even test?")
        q = add_quest(title="Are you even question?", inq=inq)
        ch = add_choice(text="Are you even test?", quest=q)
        answer = add_answer(inq_id=inq.id, quest_id=q.id, choice_id=ch.id)

        with self.client:
            response = self.client.get(f'answer/{answer.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('inq_id' in data)
            self.assertIn('quest_id', data)
            self.assertIn('user_id', data)