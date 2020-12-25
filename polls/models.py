from django.db import models
from django.utils import timezone
import datetime

# Create your models here.


class Question(models.Model):
    question_text = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return (self.question_text)
    
    def recent(self):
        return (timezone.now() >= self.pub_date >=timezone.now()-datetime.timedelta(days=1))#To see if the publication is later than 1 day or yesterday

class Choice(models.Model):
    q = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
        