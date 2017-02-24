import threading
from pymongo import MongoClient
mongo = MongoClient('mongodb://dbuser:dbpassword@ds161069.mlab.com:61069/heroku_p8hztrhs')
db = mongo.heroku_p8hztrhs

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
