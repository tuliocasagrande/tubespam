from mock import patch
from django.test import TestCase


class TubeSpamViewsTestCase(TestCase):

    @patch('app.views.youtube_api')
    def test_index_call_youtube_api_twice(self, youtube_api):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        call_count = youtube_api.get_videos_by_params.call_count
        msg = ("Expected '%s' to have been called once. Called %s times." %
               ('get_videos_by_params', call_count))

        self.assertEqual(call_count, 2, msg)

    @patch('app.views.youtube_api')
    def test_index_fetch_most_popular_on_youtube(self, youtube_api):
        self.client.get('/')

        youtube_api.get_videos_by_params.assert_called()
        most_popular_call = youtube_api.get_videos_by_params.call_args_list[1]
        call_args, _ = most_popular_call

        self.assertEqual(type(call_args[0]), dict)
        self.assertIn('chart', call_args[0])
        self.assertEqual(call_args[0]['chart'], 'mostPopular')
