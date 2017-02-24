import threading
from pymongo import MongoClient
mongo = MongoClient(mongodb://heroku_p8hztrhs:hru1a2ec3uhghi3tag1225que3@ds161069.mlab.com:61069/heroku_p8hztrhs)
db = mongo.bot_database

class Interval():
    def __init__(self, func, bot, sec=1):
        def func_wrapper():
            status = db.bot_database.find_one({'name':bot})
            if status['bot_running']:
                self.t = threading.Timer(sec, func_wrapper)
                self.t.start()
                func()
            else:
                print('stopping interval')
                self.t.cancel()

        self.t = threading.Timer(sec, func_wrapper)
        self.t.start()

    def cancel(self):
        self.t.cancel()
