import unittest, os, sys
from unittest.mock import patch, MagicMock

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from reddit_client import RedditClient
from logger import LOG  # 导入日志记录器

class TestRedditClient(unittest.TestCase):

    def test_reddit_config(self):
        '''测试环境变量是否存在'''
        self.assertTrue('REDDIT_CLIENT_ID' in os.environ)
        self.assertTrue('REDDIT_CLIENT_SECRET' in os.environ)
        self.assertTrue('OPENAI_API_KEY' in os.environ)
        self.assertTrue('GMAIL_APP_PASSWORD' in os.environ)  

    @patch('reddit_client.praw.Reddit')  # Mock praw.Reddit
    def test_fetch_hot_feeds(self, mock_reddit_class):
        '''测试获取reddit热点话题'''
        # Mock the Reddit instance
        mock_reddit_instance = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance

        # Mock the subreddit and hot methods
        mock_subreddit = MagicMock()
        mock_reddit_instance.subreddit.return_value = mock_subreddit

        # Create mock submissions
        mock_author_1 = MagicMock(name="Author1")
        mock_author_1.name = "Author1"

        mock_author_2 = MagicMock(name="Author2")
        mock_author_2.name = "Author2"

        mock_submission_1 = MagicMock(
            title="Post 1",
            subreddit=MagicMock(display_name="Group1"),
            author=mock_author_1,
            selftext="Text1",
            url="http://content_url1.com",
            permalink="/comment1",
            ups=100,
            num_comments=10,
        )
        mock_submission_2 = MagicMock(
            title="Post 2",
            subreddit=MagicMock(display_name="Group2"),
            author=mock_author_2,
            selftext="Text2",
            url="http://content_url2.com",
            permalink="/comment2",
            ups=200,
            num_comments=20,
        )
        mock_subreddit.hot.return_value = [mock_submission_1, mock_submission_2]

        # Create an instance of RedditClient
        client = RedditClient()

        # Call fetch_hot_feeds
        result = client.fetch_hot_feeds(count=2)

        # Assert the result
        self.assertEqual(len(result), 2)

        expected_feed_1 = {
            'title': "Post 1",
            'group': "Group1",
            'author': "Author1",
            'text': "Text1",
            'content_url': "http://content_url1.com",
            'comment_url': "https://www.reddit.com/comment1",
            'up_votes': 100,
            'num_comments': 10,
        }
        expected_feed_2 = {
            'title': "Post 2",
            'group': "Group2",
            'author': "Author2",
            'text': "Text2",
            'content_url': "http://content_url2.com",
            'comment_url': "https://www.reddit.com/comment2",
            'up_votes': 200,
            'num_comments': 20,
        }

        self.assertEqual(result[0], expected_feed_1)
        self.assertEqual(result[1], expected_feed_2)

        # Verify that the appropriate methods were called
        mock_reddit_instance.subreddit.assert_called_once_with("all")
        mock_subreddit.hot.assert_called_once_with(limit=2)

if __name__ == "__main__":
    unittest.main()
