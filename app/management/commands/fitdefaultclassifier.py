from django.core.management.base import BaseCommand, CommandError
from app.classification import partial_fit
from app.models import Classifier, Comment

class Command(BaseCommand):
  help = 'Fit the default classifier to make predictions'

  def handle(self, *args, **options):
    try:
      classifier = Classifier.objects.get(id='default')
    except Classifier.DoesNotExist:
      classifier = Classifier(id='default', model_filename='default_model')
      classifier.save()

    self.stdout.write('Fitting default classifier. This may take a while...')

    step = 0
    step_size = 100
    first_fit = True
    while True:
      comments = Comment.objects.all()[step:step+step_size]
      step += step_size

      if not comments:
        break

      partial_fit(classifier, comments, new_fit=first_fit)
      first_fit = False

    self.stdout.write('Finished! The default classifier is ready to make predictions!')
