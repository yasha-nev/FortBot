import json
import sys
from aiogram.types import FSInputFile


class Config:
    def __init__(self):
        self.token = ""
        self.admin_username = ""
        self.admin_tg_id = ""
        self.texts = {}
        self.expectation_photo = ""
        self.refusal_photo = ""
        self.greetings_photo = ""
        self.access_token = ""
        self.domain = ""
        self.version = ""
        self.owner_id = ""

        self.read()

    def read(self):
        self.read_config()
        self.read_texts()
        self.read_photo()

    def get_admin(self):
        return User(self.config.admin_username, self.config.admin_tg_id, True)

    def read_config(self):
        try:
            with open("configs/config.json", "r") as file:
                templates = json.load(file)
                self.token = templates["token"]
                self.admin_username = templates["admin_username"]
                self.admin_tg_id = int(templates["admin_id"])
                self.access_token = templates["access_token"]
                self.domain = templates["domain"]
                self.version = templates["version"]
                self.owner_id = templates["owner_id"]

        except FileNotFoundError:
            print("FileNotFoundError")
            sys.exit()

    def read_texts(self):
        try:
            with open("configs/texts.json", "r") as file:
                self.texts = json.load(file)
        except FileNotFoundError:
            print("FileNotFoundError")
            sys.exit()

    def read_photo(self):
        self.expectation_photo = FSInputFile("images/expectation.jpg")
        self.refusal_photo = FSInputFile("images/refusal.jpg")
        self.greetings_photo = FSInputFile("images/greetings.jpg")
