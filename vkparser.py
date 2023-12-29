import requests
from config import Config
from post import Post


class VkWallParser:
    def __init__(self, config):
        self.config = config
        self.method_get = "https://api.vk.com/method/wall.get"
        self.params = {
            "access_token": self.config.access_token,
            "v": self.config.version,
            "owner_id": self.config.owner_id,
            "domain": self.config.domain,
            "count": 1,
            "filter": "all",
        }

    def get_past_wall(self):
        self.params["count"] = 1
        response = requests.get(self.method_get, self.params)
        data = response.json()["response"]
        post = self.get_posts_from_json(data)
        return post[0]

    def get_walls(self):
        self.params["count"] = 10
        response = requests.get(self.method_get, self.params)
        data = response.json()["response"]
        posts = self.get_posts_from_json(data)
        return posts

    @staticmethod
    def get_posts_from_json(data):
        posts = []
        for item in data["items"]:
            post = Post()
            post.post_id = item["id"]
            post.text = item["text"]
            try:
                attachments = item["attachments"]
                for attach in attachments:
                    if attach["type"] == "photo":
                        count = len(attach["photo"]["sizes"])
                        post.photo = attach["photo"]["sizes"][count - 1]["url"]
            except:
                continue
            posts.append(post)

        return posts
