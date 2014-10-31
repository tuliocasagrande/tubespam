from django.db import models

class Video(models.Model):
  id = models.CharField(primary_key=True, max_length=16)
  num_untrd_comments = models.IntegerField(default=0)
  acc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
  stddev = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

  def __unicode__(self):
    return self.id

class Comment(models.Model):
  id = models.CharField(primary_key=True, max_length=64)
  author = models.TextField()
  date = models.DateTimeField()
  video_id = models.ForeignKey(Video)
  content = models.TextField()
  tag = models.BooleanField(default=False)

  def __unicode__(self):
    return self.id

  def getTag(self):
    return str(int(self.tag))

  def getEscapedContentJson(self):
    content = self.content
    content = content.replace('\\', '\\\\')
    content = content.replace('"', '\\"')
    content = content.replace('\n', ' ')
    content = content.replace('\r', ' ')
    return content.encode('utf-8')

  def getEscapedContentCsv(self):
    content = self.content
    content = content.replace('"', '""')
    content = content.replace('\n', ' ')
    content = content.replace('\r', ' ')
    return content.encode('utf-8')
