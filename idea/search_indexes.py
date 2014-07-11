from haystack import indexes
from idea.models import Idea, Banner, State, Vote, DownVote
from django.core.urlresolvers import reverse
from time import mktime, strptime
from django_cron import CronJobBase, Schedule
from django.core.mail import send_mail
from datetime import datetime, timedelta
from push_notifications.models import APNSDevice, GCMDevice
from django.contrib.auth.models import SiteProfileNotAvailable, User
from django.utils import timezone

class ArchiveIdeas(CronJobBase):
    RUN_EVERY_MINS = 10

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'AppathonWeb.idea_archive_cron_job'
    
    def do(self):
        allideas = Idea.objects.related_with_counts()
        ideas = allideas.filter(state=State.objects.get(name='Active'))
        
        for idea in ideas:
            votes = idea.voters.count() + idea.downvoters.count()
            if votes > 200: #idea needs more than 200 votes
                if (idea.voters/votes) >= 0.5: #idea needs to have 50 percent or more likes
                    send_mail('Idea has hit the threshold!', 'Idea has hit the threshold! http://ec2-54-88-16-5.compute-1.amazonaws.com/idea/detail/' + str(idea.id), 'AgilexIdeaBox@gmail.com', User.objects.filter(groups__name='BigWigs').values_list('email',flat=True), fail_silently=True)
                    devices = GCMDevice.objects.filter(user__groups__name='BigWigs')
                    devices.send_message("Idea has hit the threshold!", extra={"id": idea.id})
                    devices = APNSDevice.objects.filter(user__groups__name='BigWigs')
                    devices.send_message(None, sound="", content_available=True, extra={"id": idea.id, "msg": "Idea has hit the threshold!"})
            if  (timezone.now() - timedelta(days=7)) <= idea.time <= timezone.now():
                idea.state = State.objects.get(name='Archive')
                idea.save()
                send_mail('Idea has been Archived', 'Idea has been Archived! http://ec2-54-88-16-5.compute-1.amazonaws.com/idea/detail/' + str(idea.id), 'AgilexIdeaBox@gmail.com', User.objects.filter(groups__name='BigWigs').values_list('email',flat=True), fail_silently=True)
                devices = GCMDevice.objects.filter(user__groups__name='Approvers')
                devices.send_message("Idea has been Archived!", extra={"id": idea.id})
                devices = APNSDevice.objects.filter(user__groups__name='Approvers')
                devices.send_message(None, sound="", content_available=True, extra={"id": idea.id, "msg": "Idea has been Archived!"})

class IdeaIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    display = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr="summary", null=True)
    index_name = indexes.CharField(indexed=False)
    index_priority = indexes.IntegerField(indexed=False)
#  TODO causes all tests to fail
#    index_sort = indexes.IntegerField(indexed=False, null=True)
    url = indexes.CharField(indexed=False, null=True)

    PRIORITY = 4

    def prepare_index_name(self, obj):
        return "Ideas"

    def prepare_index_priority(self, obj):
        return self.PRIORITY

    def prepare_index_sort(self, obj):
        # want a positive number so banner results appear above/before ideas
        #9999999999 =~ year 2286
        return 9999999999 - int(mktime(strptime(obj.recent_activity, "%Y-%m-%d %H:%M:%S")))

    def prepare_url(self, obj):
        return reverse('idea:idea_detail', args=(obj.id,))

    def get_model(self):
        return Idea

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        # State 2 = Archived
        return self.get_model().objects.related_with_counts().exclude(state=2)


class BannerIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    display = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr="text")
    index_name = indexes.CharField(indexed=False)
    index_priority = indexes.IntegerField(indexed=False)
    index_sort = indexes.IntegerField(indexed=False, null=True)
    url = indexes.CharField(indexed=False, null=True)

    PRIORITY = 4

    def prepare_index_name(self, obj):
        return "Ideas"

    def prepare_index_priority(self, obj):
        return self.PRIORITY

    def prepare_index_sort(self, obj):
        return 0 - int(mktime(obj.start_date.timetuple()))

    def prepare_url(self, obj):
        return reverse('idea:banner_detail', args=(obj.id,))

    def prepare_display(self, obj):
        return "Challenge: " + obj.title

    def get_model(self):
        return Banner

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
