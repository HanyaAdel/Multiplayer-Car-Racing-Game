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
        return connection_pool
    
    def markAsOffline(self):
        self.isOnline = False
        self.needsSync = True

    def get_Connection(self) -> mysql.connector.MySQLConnection:
        return self.connection_pool.get_connection()
    
    def get(self,query,args):
        try:
            db = self.get_Connection()
            mycursor = db.cursor()
            mycursor.execute(query,args)
            result=mycursor.fetchall()
            db.close()
            self.isOnline = True
            return result
        except mysql.connector.errors.OperationalError:
            self.markAsOffline()
            return None

    def update(self,query,args):
        try:
            db = self.get_Connection()
            mycursor = db.cursor()
            mycursor.execute(query,(args))
            db.commit()
            db.close()
            self.isOnline = True
        except mysql.connector.errors.OperationalError:
            self.markAsOffline()
        except Exception as e:
            print(e)
    
    def updateMany(self,query,args):
        try:
            db = self.get_Connection()
            mycursor = db.cursor()
            mycursor.executemany(query,args)
            db.commit()
            db.close()
            self.isOnline = True
        except mysql.connector.errors.OperationalError:
            self.markAsOffline()
        except Exception as e:
            print(e)
