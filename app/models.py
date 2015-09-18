from django.db import models

class Classifier(models.Model):
  id = models.CharField(primary_key=True, max_length=32)
  model_filename = models.CharField(max_length=48, null=True, blank=True)

  def __unicode__(self):
    return unicode(self.id)

class Video(models.Model):
  id = models.CharField(primary_key=True, max_length=16)
  channel_id = models.CharField(max_length=32)

  def __unicode__(self):
    return unicode(self.id)

class Comment(models.Model):
  id = models.CharField(primary_key=True, max_length=64)
  author = models.TextField()
  date = models.DateTimeField()
  video = models.ForeignKey(Video)
  content = models.TextField()
  tag = models.BooleanField(default=False)

  def __unicode__(self):
    return unicode(self.id)
