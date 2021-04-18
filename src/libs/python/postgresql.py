
import time
import psycopg2

import util

class PostgreSQL:
    cursor = None
    connection = None
    host = ''
    db = ''
    user = ''
    passwd = ''
    topic = ''

    def __init__(self, host, user, passwd, db, topic):
        self.host = host
        self.user = user
        self.passwd =  passwd
        self.db = db
        self.topic = topic
        self.connect_inifloop()
    
    def connect_inifloop(self):
        while True:
            if self.connect():
                break
            util.eprint("Can't connect to {self.host}. try again")
            time.sleep(10)

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host = self.host,
                database =  self.db,
                user =  self.user,
                password = self.passwd)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            util.eprint(f"Connect to DB on {self.host}, db {self.db}")
            return True
        except:
            util.lprint()
            return False
    
    def insert_row(self, table, row, retry = True):
        try:
            self.cursor.execute(row)
            util.eprint(f"Insert row: {row}")
        except psycopg2.InterfaceError:  # Connection problem!
            util.lprint()
            if self.connect():
                if retry:
                    self.insert_row(table, row, False)
        except psycopg2.ProgrammingError: # Table not exists (maybe)
            util.lprint()
            self.create_table(table)
            if retry:
                self.insert_row(table, row, False)
        except:
            util.lprint()
    
    def create_table(self, table):
        try:
            if self.topic == 'segment_info':
                table_struct = ( f"create table {table} ("+
                    "ID        SERIAL PRIMARY KEY," +
                    "channel   varchar(127)," +
                    "sequence  int," +
                    "start     real," +
                    "duration  real)" )
                self.cursor.execute(table_struct)
                util.eprint(f"Create Table {table}")
        except:
            util.lprint()
        
