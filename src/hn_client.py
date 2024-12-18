import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class HackerNewsClient:

    def __init__(self):
        self.url = 'https://news.ycombinator.com/'

    def fetch_hackernews_top_stories(self):
        response = requests.get(self.url)
        response.raise_for_status()  # 检查请求是否成功

        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找包含新闻的所有 <tr> 标签
        stories = soup.find_all('tr', class_='athing')

        top_stories = []
        for story in stories:
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                top_stories.append({'title': title, 'link': link})

        return top_stories
    
    def save_stories(self, stories, folder_name='daily_progress'):
        hn_dir = os.path.join(folder_name, 'hacker_news')
        if not os.path.exists(hn_dir):
            os.mkdir(hn_dir)
        
        today = datetime.now().date().isoformat()
        hn_path = os.path.join(hn_dir, today+'.json')
        with open(hn_path, 'w') as f:
            json.dump(stories, f, ensure_ascii=False, indent=4)

        return hn_path


if __name__ == "__main__":
    client = HackerNewsClient()
    stories = client.fetch_hackernews_top_stories()
    if stories:
        for idx, story in enumerate(stories, start=1):
            print(f"{idx}. {story['title']}")
            print(f"   Link: {story['link']}")
    else:
        print("No stories found.")