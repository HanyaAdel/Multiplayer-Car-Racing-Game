import mysql.connector.pooling
import os

from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self, isPrimary:bool) -> None:
        self.isOnline = False
        self.needsSync = False
        self.connection_pool = self.create_connection_pool(isPrimary = isPrimary)

    def create_connection_pool(self, isPrimary):
        print("trying to create connection pool")
        db_config = None
        if isPrimary:
            db_config = {
                "host":os.getenv('PRIMARY_DB_HOST'),
                "user":os.getenv('PRIMARY_DB_USER'),
                'password':os.getenv('PRIMARY_DB_PASSWD'),
                'database':os.getenv('PRIMARY_DB_DATABASE')
            }
        else:
            db_config = {
                "host":os.getenv('SECONDARY_DB_HOST'),
                "user":os.getenv('SECONDARY_DB_USER'),
                'password':os.getenv('SECONDARY_DB_PASSWD'),
                'database':os.getenv('SECONDARY_DB_DATABASE')
            }
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "mypool",
            pool_size = 5,
            autocommit = True,
            **db_config
        )
        print("created connection pool")
        return connection_pool
    
    def markAsOffline(self):
        self.isOnline = False
        self.needsSync = True

    def get_Connection(self):
        return self.connection_pool.get_connection()
    
    def get(self,query,args):
        try:
            print("in begining of get try")
            db = self.get_Connection()
            mycursor = db.cursor()
            mycursor.execute(query,args)
            result=mycursor.fetchall()
            db.close()
            self.isOnline = True
            print("in end of get try")
            return result
        except mysql.connector.errors.InterfaceError:
            self.markAsOffline()
            print ("in get interface exception")
            return None
        except Exception as e:
            print ("in get e exception")

    def update(self,query,args):
        try:
            print("in begining of update try")
            db = self.get_Connection()
            mycursor = db.cursor()
            mycursor.execute(query,(args))
            db.commit()
            db.close()
            self.isOnline = True
            print("in end of update try")
        except mysql.connector.errors.InterfaceError:
            self.markAsOffline()
            print ("in update interface exception")
        except Exception as e:
            print ("in update e exception")
            #print(type(e).__name__)
    
    def updateMany(self,query,args):
        try:
            print("in begining of update many try")
            db = self.get_Connection()
            mycursor = db.cursor()
            mycursor.executemany(query,args)
            db.commit()
            db.close()
            self.isOnline = True
            print("in end of update many try")
        except mysql.connector.errors.InterfaceError:
            print ("in update many interface exception")
            self.markAsOffline()
        except Exception as e:
            print ("in update many e exception")
            print(e)
