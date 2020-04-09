import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


# Create your tests here.

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question(question_text=question_text, pub_date=time)
    question.save()
    return question


class QuestionViewIndex(TestCase):
    def test_no_question(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Polls Available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        create_question(question_text='an old question', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: an old question>'])

    def test_future_question(self):
        create_question(question_text='Future Question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No Polls Available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_question(self):
        create_question(question_text='Future Question', days=30)
        create_question(question_text='an old question', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: an old question>'])

    def test_past_two_questions(self):
        create_question(question_text='Past Question 1', days=-30)
        create_question(question_text='Past Question 2', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question 2>',
                                                                            '<Question: Past Question 1>'])


class QuestionModelTest(TestCase):

    def test_was_published_future(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_correctly(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class TestDetailView(TestCase):
    def test_future_date(self):
        question = create_question(question_text='New One', days=5)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_date(self):
        question = create_question(question_text='New One', days=-5)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
