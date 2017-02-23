import threading
from pymongo import MongoClient
mongo = MongoClient()
db = mongo.bot_database

class Interval():
    def __init__(self, func, sec=1):
        def func_wrapper():
            if db.is_running.count() == 1:
                self.t = threading.Timer(sec, func_wrapper)
                self.t.start()
                print('doing interval')
                func()
            else:
                print('stopping interval')
                self.t.cancel()

        self.t = threading.Timer(sec, func_wrapper)
        self.t.start()

    def cancel(self):
        self.t.cancel()
