import mysql.connector.pooling
import os

from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self, isPrimary:bool) -> None:
        self.isOnline = False
        self.needsSync = False
        self.connection_pool = self.create_connection_pool(isPrimary = isPrimary)
        self.test_connection = mysql.connector.connect(**self.get_db_config(isPrimary=isPrimary))
        print("is test connection connected: ", self.test_connection.is_connected())

    def get_db_config(self, isPrimary):
        db_config = {}
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
        
        return db_config
        
    def create_connection_pool(self, isPrimary):
        print("trying to create connection pool")
        db_config = self.get_db_config(isPrimary)

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
        db = None
        try:
            
            #print("before get getting connection")
            db = self.get_Connection()
            #print("after get getting connection")
            mycursor = db.cursor()
            #print("before get execute")
            mycursor.execute(query,args)
            #print("after get execute")
            result=mycursor.fetchall()
            self.isOnline = True
            #print("in end of get try")
            return result
        except mysql.connector.errors.InterfaceError:
            self.markAsOffline()
            print ("in get interface exception")
            return None
        except Exception as e:
            print(e)
            self.markAsOffline()
            print ("in get e exception")
        finally:
            if db and self.isOnline:
                db.close()

    def truncateAll(self):
        db = None
        try:
            print("in begining of truncate all")
            db = self.get_Connection()
            mycursor = db.cursor()
            table_list = ['message_in_session', 'player_in_session','player', 'session']
            for table in table_list:
                print(f"in table {table}")
                query = f"DELETE FROM {table};"
                mycursor.execute(query)
            db.commit()
            self.isOnline = True

        except mysql.connector.errors.InterfaceError:
            self.markAsOffline()
            print ("in update interface exception")
        except Exception as e:
            print(e)
            self.markAsOffline()
            print ("in update e exception")
            #print(type(e).__name__)
        finally:
            if db and self.isOnline:
                db.close()

    def update(self,query,args):
        db = None
        try:
            #print("in begining of update try")
           # print("before update getting connection")
            db = self.get_Connection()
            #print("after update getting connection")
            mycursor = db.cursor()
            #print("before update execute")
            mycursor.execute(query,(args))
            #print("after update execute")
            db.commit()
            self.isOnline = True
            #print("in end of update try")
        except mysql.connector.errors.InterfaceError:
            self.markAsOffline()
            print ("in update interface exception")
        except Exception as e:
            print(e)
            self.markAsOffline()
            print ("in update e exception")
            #print(type(e).__name__)
        finally:
            if db and self.isOnline:
                db.close()            
    
    def updateMany(self,query,args):
        db = None
        try:
            #print("in begining of update many try")
            #print("before update many getting connection")
            db = self.get_Connection()
            #print("after update many getting connection")
            mycursor = db.cursor()
            #print("before update many execute")
            mycursor.executemany(query,args)
            #print("after update many execute")
            db.commit()
            self.isOnline = True
            #print("in end of update many try")
        except mysql.connector.errors.InterfaceError:
            print ("in update many interface exception")
            self.markAsOffline()
        except Exception as e:
            self.markAsOffline()
            print ("in update many e exception")
            print(e)
        finally:
            if db and self.isOnline:
                db.close()            
