import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters.command import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from config import Config
from db import DB, User
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from vkparser import VkWallParser, Post

logging.basicConfig(level=logging.INFO)


class UserRouter(Router):
    def __init__(self, config, db, not_users_list, bot):
        super().__init__()
        self.db = db
        self.config = config
        self.not_add_users = not_users_list
        self.bot = bot
        self.init_handlers()

    def init_handlers(self):
        self.message.register(self.subscribe_handler, F.text.lower() == "подписаться")
        self.message.register(self.unsubscribe_handler, F.text.lower() == "отписаться")

    async def subscribe_handler(self, message: Message):
        user = User(message.from_user.username, message.from_user.id)
        if self.db.check_exists(user):
            posts = self.bot.parser.get_walls()
            await message.reply(self.config.texts['already_subscribe'])
            for post in posts:
                await self.bot.send_post_message(user, post)
        else:
            self.not_add_users.append(user)
            await message.answer_photo(photo=self.config.expectation_photo,
                                       caption=self.config.texts['request_admin_from_user'])
            await self.user_add_handler(user)

    async def unsubscribe_handler(self, message: Message):
        user = User(message.from_user.username, message.from_user.id)
        if self.db.check_exists(user):
            self.db.delete_user(User(message.from_user.first_name, message.from_user.id))
            await message.reply(self.config.texts['unsubscribe'])
        else:
            await message.reply(self.config.texts['not_subscribe_yet'])

    async def user_add_handler(self, user):
        admin = self.db.get_admins()[0]
        kb = [
            [KeyboardButton(text="Добавить")],
            [KeyboardButton(text="Не добавлять")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await self.bot.send_message(admin.tg_id,
                                    text=self.config.texts['request_admin_from_bot'] + user.name,
                                    reply_markup=keyboard)


class AdminRouter(Router):
    def __init__(self, config, db, not_users_list, bot):
        super().__init__()
        self.db = db
        self.config = config
        self.not_add_users = not_users_list
        self.bot = bot
        self.init_handlers()

    def init_handlers(self):
        self.message.register(self.admin_add_user, F.text.lower() == "добавить")
        self.message.register(self.admin_del_user, F.text.lower() == "не добавлять")

    async def admin_add_user(self, message: Message):
        if len(self.not_add_users) == 0:
            return

        user = self.not_add_users.pop(0)
        self.db.add_user(user)

        posts = self.bot.parser.get_walls()

        for post in posts:
            await self.bot.send_post_message(user, post)

    async def admin_del_user(self, message: Message):
        if len(self.not_add_users) == 0:
            return

        user = self.not_add_users.pop(0)
        await self.bot.send_photo(user.tg_id,
                                  photo=self.config.refusal_photo,
                                  caption=self.config.texts['refusal'])


class FortBot(Bot):
    def __init__(self, conf):
        super().__init__(token=conf.token)
        self.dispatcher = Dispatcher()
        self.config = conf
        self.db = DB()
        self.not_add_users = []
        self.last_post = Post()
        self.db.add_user(User(self.config.admin_username, self.config.admin_tg_id, True))
        self.init_handles()
        self.parser = VkWallParser(conf)

    def init_handles(self):
        self.dispatcher.message.register(self.start_handler, Command("start"))
        self.dispatcher.include_router(UserRouter(self.config, self.db, self.not_add_users, self))
        self.dispatcher.include_router(AdminRouter(self.config, self.db, self.not_add_users, self))

    async def check_new_post(self):
        post = self.parser.get_past_wall()

        if post.post_id == self.last_post.post_id or post.text == '' or post.photo == '':
            return

        self.last_post = post

        for user in self.db.get_users_list():
            await self.send_post_message(user, post)

    async def send_post_message(self, user, post):
        if post.text == '':
            return

        elif post.photo == '':
            count = int(len(post.text) / 1000) + 1
            for i in range(count):
                await self.send_message(user.tg_id, text=post.text[i * 1000:(i+1) * 1000])
        else:
            count = int(len(post.text) / 1000) + 1
            for i in range(count):
                if i == count - 1:
                    await self.send_photo(user.tg_id,
                                          photo=post.photo,
                                          caption=post.text[i * 1000:(i+1) * 1000])
                    break

                await self.send_message(user.tg_id, text=post.text[i * 1000:(i+1) * 1000])

    async def start(self):
        await self.dispatcher.start_polling(self)

    async def start_handler(self, message: Message):
        kb = [
            [KeyboardButton(text="Подписаться")],
            [KeyboardButton(text="Отписаться")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer_photo(photo=self.config.greetings_photo,
                                   reply_markup=keyboard,
                                   caption=self.config.texts['greetings'])


async def main():
    conf = Config()
    bot = FortBot(conf)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(bot.check_new_post, 'interval', seconds=60 * 15)
    scheduler.start()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
