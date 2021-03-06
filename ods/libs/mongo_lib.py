# coding=utf-8

"""
    author : niyoufa
    date : 2016-05-20

"""

import pymongo, pdb

SERVER_MONGODB_HOST = "localhost"
SERVER_MONGODB_PORT = 27017
SERVER_MONGODB_USER = ""
SERVER_MONGODB_PASS = ""

class DB_CONST:
    DB_NAME = "db_name"
    COLL_NAME = "coll_name"
    COLL_HOST = "host"
    COLL_PORT = "port"
    USERNAME = "username"
    PASSWORD = "password"
    COLL_TYPE = "coll_type"


class Collections:
    # MongoDB文档配置
    __COLLECTIONS = dict(

        goods=dict(
            coll_name="goods",
            db_name="jxfresh",
            host=SERVER_MONGODB_HOST,
            port=SERVER_MONGODB_PORT,
            username=SERVER_MONGODB_USER,
            password=SERVER_MONGODB_PASS,
            coll_type=None),
    )

    @classmethod
    def get_db_name(cls, table_name):
        if cls.__COLLECTIONS.has_key(table_name):
            db_name = cls.__COLLECTIONS[table_name][DB_CONST.DB_NAME]
        else:
            db_name = ""
        return db_name

    @classmethod
    def get_coll_name(cls, table_name):
        if cls.__COLLECTIONS.has_key(table_name):
            coll_name = cls.__COLLECTIONS[table_name][DB_CONST.COLL_NAME]
        else:
            coll_name = ""
        return coll_name

    @classmethod
    def get_coll_host(cls, table_name):
        if cls.__COLLECTIONS.has_key(table_name):
            coll_host = cls.__COLLECTIONS[table_name][DB_CONST.COLL_HOST]
        else:
            coll_host = ""
        return coll_host

    @classmethod
    def get_coll_port(cls, table_name):
        if cls.__COLLECTIONS.has_key(table_name):
            coll_port = cls.__COLLECTIONS[table_name][DB_CONST.COLL_PORT]
        else:
            coll_port = ""
        return coll_port

    @classmethod
    def get_coll_username(cls, table_name):
        if cls.__COLLECTIONS.has_key(table_name):
            username = cls.__COLLECTIONS[table_name][DB_CONST.USERNAME]
        else:
            username = ""
        return username

    @classmethod
    def get_coll_password(cls, table_name):
        if cls.__COLLECTIONS.has_key(table_name):
            password = cls.__COLLECTIONS[table_name][DB_CONST.PASSWORD]
        else:
            password = ""
        return password


def get_client(table_name):
    host = Collections.get_coll_host(table_name)
    port = Collections.get_coll_port(table_name)
    client = pymongo.MongoClient(host, port)
    return client

coll_dict = {}

def get_coll(table_name):
    if coll_dict.has_key((table_name)):
        return coll_dict[table_name]
    else:
        db_name = Collections.get_db_name(table_name)
        coll_name = Collections.get_coll_name(table_name)
        username = Collections.get_coll_username(table_name)
        password = Collections.get_coll_password(table_name)
        if db_name and coll_name:
            if username and password:
                client = get_client(table_name)
                db = client[db_name]
                db.authenticate(username, password)
                coll = client[db_name][coll_name]
            else:
                client = get_client(table_name)
                coll = client[db_name][coll_name]
        else:
            coll = None
            print u"集合不存在!"
            return coll
        coll_dict[table_name] = coll
        return coll