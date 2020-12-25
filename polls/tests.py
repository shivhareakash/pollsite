from django.test import TestCase

# Create your tests here.
import datetime
from django.utils import timezone

from .models import Question, Choice
from django.urls import reverse


class Question_model_test(TestCase):
    def test_1_check_for_future_pub_date(self):
        future_time = timezone.now()+datetime.timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertIs(future_question.recent(), False)

    def test_2_check_for_old_date(self):
        old_date= timezone.now()-datetime.timedelta(days=1, seconds=1)
        old_question= Question(pub_date=old_date)
        self.assertIs(old_question.recent(), False)
    
    def test_3_check_for_recent_date(self):
        recent_date = timezone.now()-datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question= Question(pub_date=recent_date)
        self.assertIs(recent_question.recent(), True)


def create_question(question_text, days):
    date = timezone.now()+datetime.timedelta(days=days)
    Question.objects.create(question_text=question_text, pub_date=date)

def create_choice(question_id, choice_text, votes):
    q = Question.objects.get(id=question_id)
    q.choice_set.create(choice_text=choice_text,votes=votes)

class Question_Indexview_test(TestCase):

    def test_no_questions(self):
            """
            If no questions exist, an appropriate message is displayed.
            """
            response = self.client.get(reverse('polls:index'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "No polls are available")
            self.assertQuerysetEqual(response.context_data['latest_question_list'], [])

    def test_past_question(self):
        create_question(question_text="past q1", days=-20)
        create_choice(question_id=Question.objects.get(question_text="past q1").id, choice_text="option 1", votes=0)

        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "past q1")
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['latest_question_list'], ['<Question: past q1>'])

    def test_future_question(self):
        create_question(question_text="future q1", days=20)
        create_choice(question_id=Question.objects.get(question_text="future q1").id, choice_text="option 1", votes=0)

        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context_data['latest_question_list'], [])

    def test_past_and_future_question(self):
        create_question(question_text="past q2", days=-20)
        create_choice(question_id=Question.objects.get(question_text="past q2").id, choice_text="option 1", votes=0)
        create_question(question_text="future q2", days=20)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "past q2")
        self.assertQuerysetEqual(response.context_data['latest_question_list'],['<Question: past q2>'])

    def test_two_past_question(self):
        create_question(question_text="past q1", days=-20)
        create_choice(question_id=Question.objects.get(question_text="past q1").id, choice_text="option 1", votes=0)
        create_question(question_text='past q2', days=-30)
        create_choice(question_id=Question.objects.get(question_text="past q2").id, choice_text="option 1", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'past q1')
        self.assertContains(response,'past q2')
        self.assertQuerysetEqual(response.context_data['latest_question_list'],  ['<Question: past q1>', '<Question: past q2>'])

    
class Question_detailview_test(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        create_question(question_text="Future Q", days=30)
        future_question = Question.objects.get(question_text="Future Q")
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)


    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        create_question(question_text="Past Q", days=-30)
        past_question = Question.objects.get(question_text="Past Q")
        create_choice(question_id=Question.objects.get(question_text="Past Q").id, choice_text="option 1", votes=0)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)
    
class Question_resultview_test(TestCase):
    def test_future_question(self):
        """
        The result view of a question with a pub_date in the future
        displays the question's text.
        """
        create_question(question_text="future q", days=30)
        future_question= Question.objects.get(question_text='future q')
        response = self.client.get(reverse("polls:results", args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):

        """
        The result view of a question with a pub_date in the past
        displays the question's text.
        """
        create_question(question_text="past q", days=-20)
        past_question = Question.objects.get(question_text="past q")
        create_choice(question_id=Question.objects.get(question_text="past q").id, choice_text="option 1", votes=0)
        response = self.client.get(reverse("polls:results", args=(past_question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question)
        

class Question_listview_withoutChoice_test(TestCase):
    """Check if Questions can be published on the site that have no Choices."""
    def test_check_question_no_choice(self):
        create_question(question_text="Gary q", days=-20)
        #not creating any choice
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")

    def test_one_question_with_choice_one_with_not(self):
        create_question(question_text="Top brands", days=-20)
        create_choice(question_id=Question.objects.get(question_text="Top brands").id,choice_text="Ericsson",votes=0)

        create_question(question_text="Top shoes", days=-20)
        #not creating any choice

        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Top brands")


class Question_detailview_withoutChoice_test(TestCase):
    def test_check_question_no_choice(self):
        create_question(question_text="Gary q", days=-20)
        #not creating any choice
        response = self.client.get(reverse("polls:detail", args=(Question.objects.get(question_text="Gary q").id,)))
        self.assertEqual(response.status_code, 404)
      

    def test_question_with_choice(self):
        create_question(question_text="Top brands", days=-20)
        create_choice(question_id=Question.objects.get(question_text="Top brands").id,choice_text="Ericsson",votes=0)

        response = self.client.get(reverse("polls:detail", args=(Question.objects.get(question_text="Top brands").id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Top brands")

class Question_resultview_withoutChoice_test(TestCase):
    def test_check_question_no_choice(self):
        create_question(question_text="Gary q", days=-20)
        #not creating any choice
        response = self.client.get(reverse("polls:results", args=(Question.objects.get(question_text="Gary q").id,)))
        self.assertEqual(response.status_code, 404)
      

    def test_question_with_choice(self):
        create_question(question_text="Top brands", days=-20)
        create_choice(question_id=Question.objects.get(question_text="Top brands").id,choice_text="Ericsson",votes=0)

        response = self.client.get(reverse("polls:results", args=(Question.objects.get(question_text="Top brands").id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Top brands")
