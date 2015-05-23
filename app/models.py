from django.db import models

class Video(models.Model):
  id = models.CharField(primary_key=True, max_length=16)
  num_untrd_comments = models.IntegerField(default=0)
  acc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
  stddev = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

  def __unicode__(self):
    return unicode(self.id) or u''

class Comment(models.Model):
  id = models.CharField(primary_key=True, max_length=64)
  author = models.TextField()
  date = models.DateTimeField()
  video = models.ForeignKey(Video)
  content = models.TextField()
  tag = models.BooleanField(default=False)

  def __unicode__(self):
    return self.id

  def getTag(self):
    return str(int(self.tag))

  def toJson(self, attr):
    string = getattr(self, attr)
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    string = string.replace('\n', ' ')
    string = string.replace('\r', ' ')
    return string.encode('utf-8')

  def toCsv(self, attr):
    string = getattr(self, attr)
    string = string.replace('"', '""')
    string = string.replace('\n', ' ')
    string = string.replace('\r', ' ')
    return string.encode('utf-8')
