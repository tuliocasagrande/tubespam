from django.db import models

class Video(models.Model):
  id = models.CharField(primary_key=True, max_length=16)

  def __unicode__(self):
        return self.id

class Comment(models.Model):
  id = models.CharField(primary_key=True, max_length=64)
  video_id = models.ForeignKey(Video)
  content = models.TextField()
  tag = models.BooleanField(default=0)

  def __unicode__(self):
        return self.id
