import requests  # 导入requests库用于HTTP请求
from bs4 import BeautifulSoup  # 导入BeautifulSoup库用于解析HTML内容
from datetime import datetime  # 导入datetime模块用于获取日期和时间
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块
import praw
import json

'''
先创建reddit应用，这里是说明文档：
https://www.reddit.com/prefs/apps/

其中type选择script, redirect uri没有的话可以填写http://localhost:8080
创建成功后保存client_id, secret

安装reddit客户端:
pip install praw
'''

class RedditClient:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.environ.get('REDDIT_CLIENT_ID', ''),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET', ''),
            user_agent='feed_reporter by ghs homework',
        )

    def fetch_hot_feeds(self, count=5):
        LOG.debug("准备获取Reddit的热门帖子。")
        try:
            submissions = self.reddit.subreddit("all").hot(limit=count)
            feeds = list(map(self.get_feed_info, submissions))
            LOG.info(f"成功获取 {len(feeds)} 条Reddit热帖。")
            return feeds
        except Exception as e:
            LOG.error(f"获取Reddit的热门帖子失败：{str(e)}")
            return []

    @staticmethod
    def get_feed_info(submission):
        feed = {}
        feed['title'] = submission.title
        feed['group'] = submission.subreddit.display_name
        feed['author'] = submission.author.name
        feed['text'] = submission.selftext
        feed['content_url'] = submission.url
        feed['comment_url'] = 'https://www.reddit.com' + submission.permalink
        feed['up_votes'] = submission.ups
        feed['num_comments'] = submission.num_comments
        return feed

    def export_feeds(self, feeds, date=None, hour=None):
        LOG.debug("准备导出Reddit的热门帖子。")
        
        if not feeds:
            LOG.warning("未找到任何Reddit的帖子。")
            return None
        
        # 如果未提供 date 和 hour 参数，使用当前日期和时间
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if hour is None:
            hour = datetime.now().strftime('%H')

        # 构建存储路径
        dir_path = os.path.join('reddit', date)
        os.makedirs(dir_path, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(dir_path, f'{hour}.md')  # 定义文件路径
        with open(file_path, 'w') as file:
            file.write(f"# Reddit hot feeds ({date} {hour}:00)\n\n")
            for feed in feeds:
                lines = []
                lines.append(f"#### [{feed['title']}]({feed['comment_url']})")
                if feed['text']:
                    lines.append(f"{feed['text']}")
                if "image_description" in feed:
                    lines.append(f"![image]({feed['content_url']})")
                    lines.append(f"With image described: " + feed['image_description'])
                file.write('\n'.join(lines) + '\n\n')

        # 顺便保存一份json数据（备份）
        json_path = os.path.join(dir_path, f'{hour}.json')
        with open(json_path, 'w') as file:
            json.dump(feeds, file, ensure_ascii=False, indent=4)
        
        LOG.info(f"Reddit的热帖文件生成：{file_path}")
        return file_path
    
    def test_file_path(self):
        return os.path.join('reddit', '2024-12-21', '15.md')
    

if __name__ == '__main__':
    client = RedditClient()
    feeds = client.fetch_hot_feeds(count=5)
    print(json.dumps(feeds, ensure_ascii=False, indent=4))