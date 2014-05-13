from django.db import models

class Video(models.Model):
  id = models.CharField(primary_key=True, max_length=16)

  def __unicode__(self):
        return self.id

class Comment(models.Model):
  id = models.CharField(primary_key=True, max_length=64)
  video_id = models.ForeignKey(Video)
  content = models.TextField()
  tag = models.BooleanField()

  def __unicode__(self):
    return self.id

  def getTag(self):
    return str(int(self.tag))

  def getEscapedContent(self):
    content = self.content
    content = content.replace('\\', '\\\\')
    content = content.replace('"', '\\"')
    content = content.replace('\n', ' ')
    content = content.replace('\r', ' ')
    return content.encode('utf-8')
