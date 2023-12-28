import psycopg2
from psycopg2 import Error
from user import User
import os


class DB:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                user=os.environ.get("POSTGRES_USER"),
                password=os.environ.get("POSTGRES_PASSWORD"),
                host="postgres",
                port="5432",
                database=os.environ.get("POSTGRES_DB"),
            )

            self.cursor = self.connection.cursor()

        except (Exception, Error) as error:
            log(error)
            return

        self.create_user_table()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def create_user_table(self):
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS USERS(
                             ID SERIAL PRIMARY KEY NOT NULL,
                             name TEXT NOT NULL,
                             tg_id TEXT NOT NULL,
                             admin BOOLEAN NOT NULL
                             );
                             """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
        except (Exception, Error) as error:
            log(error)

    def add_user(self, user):
        if self.check_exists(user):
            return

        insert_user_query = """
                            INSERT INTO USERS (name, tg_id, admin)
                            VALUES(%s, %s, %s)
                            """
        try:
            self.cursor.execute(
                insert_user_query, (user.name, str(user.tg_id), user.admin)
            )
            self.connection.commit()
        except (Exception, Error) as error:
            log(error)

    def delete_user(self, user):
        if not self.check_exists(user):
            return

        delete_user_query = """
                            DELETE FROM USERS where name=%s AND tg_id=%s
                            """
        try:
            self.cursor.execute(
                delete_user_query,
                (
                    user.name,
                    str(user.tg_id),
                ),
            )
            self.connection.commit()
        except (Exception, Error) as error:
            log(error)

    def get_users_list(self):
        users = []
        records = []
        select_user_query = """
                            SELECT * FROM USERS
                            """
        try:
            self.cursor.execute(select_user_query)
            records = self.cursor.fetchall()
        except (Exception, Error) as error:
            log(error)

        for rec in records:
            users.append(User(rec[1], rec[2], rec[3]))

        return users

    def check_exists(self, user):
        records = []
        select_user_query = """
                            SELECT * FROM USERS WHERE name=%s AND tg_id=%s
                            """
        try:
            self.cursor.execute(
                select_user_query,
                (
                    user.name,
                    str(user.tg_id),
                ),
            )
            records = self.cursor.fetchall()
        except (Exception, Error) as error:
            log(error)

        if len(records) == 0:
            return False

        return True

    def check_admin(self, user):
        records = []
        select_user_query = """
                            SELECT * FROM USERS WHERE name=%s AND tg_id=%s AND admin=TRUE
                            """
        try:
            self.cursor.execute(
                select_user_query, (user.name, str(user.tg_id), user.admin)
            )
            records = self.cursor.fetchall()
        except (Exception, Error) as error:
            log(error)

        if len(records) == 0:
            return False

        return True

    def get_admins(self):
        admins = []
        records = []
        select_user_query = """
                            SELECT * FROM USERS WHERE admin=TRUE
                            """
        try:
            self.cursor.execute(select_user_query)
            records = self.cursor.fetchall()
        except (Exception, Error) as error:
            log(error)

        for rec in records:
            admins.append(User(rec[1], rec[2], rec[3]))

        return admins

    def set_admin(self, user):
        query = """
                UPDATE USERS
                SET admin=TRUE
                WHERE name=%s AND tg_id=%s
                """
        try:
            self.cursor.execute(query, (user.name, user.tg_id))
            self.connection.commit()
        except (Exception, Error) as error:
            log(error)


def log(error):
    print("postgreSQL error: ", error)
