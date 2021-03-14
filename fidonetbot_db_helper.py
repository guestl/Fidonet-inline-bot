# -*- coding: utf-8 -*-

# helper for work with database
import sqlite3

import config

import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(config.LOGGER_LEVEL)


os.chdir(os.path.dirname(os.path.abspath(__file__)))


class fidonetbot_db_helper:
    """class helper for work with SQLite3 database

    methods:
        __init__ -- setup db setting
        add_currency_rates_data -- insert parsed data into rates table
    """

    def __init__(self, dbname=config.dbname):
        self.dbname = dbname
        logger.debug(dbname)
        try:
            self.connection = sqlite3.connect(dbname, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logger.error(dbname)
            logger.error(e)
            raise e

    # I got this piece of code from
    #    http://stackoverflow.com/questions/5266430/how-to-see-the-real-sql-query-in-python-cursor-execute"
    # it doesn't work pretty good,
    #   but I can see a sql text and it's enough for me
    def check_sql_string(self, sql_text, values):
        unique = "%PARAMETER%"
        sql_text = sql_text.replace("?", unique)
        for v in values:
            sql_text = sql_text.replace(unique, repr(v), 1)
        return sql_text

# search is case insensitive
    def get_fidodata_by_text(self, tg_data):
        result = []

        try:
            sql_text = 'SELECT fido_addr, fido_name, tg_username, tg_name \
                FROM fidonetlist\
                WHERE tg_name LIKE "%{data}%" \
                or tg_username LIKE "%{data}%" \
                or fido_addr LIKE "%{data}%" \
                or fido_name LIKE "%{data}%" \
                order by fido_addr LIMIT 10\
                COLLATE NOCASE'.format(data=tg_data)

#            logger.info(sql_text)
            self.cursor.execute(sql_text)
        except Exception as e:
            logger.error(e)
            logger.error(self.check_sql_string(sql_text))

        if self.cursor:
            for row in self.cursor:
                logger.info(row)
                title = row[0] + ", " + row[1]
                data = row[0] + ", " + row[1]
                if (row[2] is not None):
                    data = data + (", @" + row[2])
                    result.append({'title': title, 'data': data})
                if (row[3] is not None):
                    data = data + (", @" + row[3])
                    result.append({'title': title, 'data': data})

        logger.info(result)
        return result
