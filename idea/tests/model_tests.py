from django.test import TestCase
from idea import models
from idea.tests.utils import random_user
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment


class VotingTests(TestCase):
    fixtures = ['state', 'core-test-fixtures']

    def setUp(self):
        self.state = models.State.objects.get(name='Active') 

    def test_members(self):
        user = random_user()
        idea = models.Idea(creator=user, title='Transit subsidy to Mars', 
                    text='Aliens need assistance.', state=self.state)
        idea.save()
        
        self.assertEqual(len(idea.members), 1)
        self.assertIn(user, idea.members)

    def test_members_with_voters(self):
        user = random_user()
        idea = models.Idea(creator=user, title='Transit subsidy to Mars', 
                    text='Aliens need assistance.', state=self.state)
        idea.save()
        
        voter = User.objects.get(username='test1@example.com')
        vote = models.Vote()
        vote.idea = idea
        vote.creator = voter
        vote.save()

        self.assertEqual(len(idea.members), 1)
        self.assertNotIn(voter, idea.members)
        self.assertIn(user, idea.members)

    def test_members_with_comments(self):
        user = random_user()
        idea = models.Idea(creator=user, title='Transit subsidy to Mars',
                    text='Aliens need assistance.', state=self.state)
        idea.save()
        
        commenter = User.objects.get(username='test1@example.com')

        comment = Comment()
        comment.user = commenter
        comment.content_object = idea
        comment.comment = 'Test'
        comment.is_public = True
        comment.is_removed = False
        comment.site_id = 1
        comment.save()

        self.assertEqual(len(idea.members), 2)
        self.assertIn(commenter, idea.members)
        self.assertIn(user, idea.members)

    def test_members_with_comment_by_same_user(self):
        user = random_user()
        idea = models.Idea(creator=user, title='Transit subsidy to Mars',
                    text='Aliens need assistance.', state=self.state)
        idea.save()

        commenter = user

        comment = Comment()
        comment.user = commenter
        comment.content_object = idea
        comment.comment = 'Test'
        comment.is_public = True
        comment.is_removed = False
        comment.site_id = 1
        comment.save()

        self.assertEqual(len(idea.members), 1)
        self.assertIn(user, idea.members)
