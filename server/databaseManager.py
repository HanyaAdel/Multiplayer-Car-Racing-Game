import threading
import time
from database import Database

class DatabaseManager:
    def __init__(self) -> None:
        self.primary_database = Database(isPrimary=True)
        self.secondary_database = Database(isPrimary=False)
        self.table_list = ["player", "session", "message_in_session", "player_in_session"]
        self.primary_reconnection_thread = threading.Thread(target=self.primary_reconnect, daemon=True)
        self.secondary_reconnection_thread = threading.Thread(target=self.secondary_reconnect, daemon=True)

        self.primary_reconnection_thread.start()
        self.secondary_reconnection_thread.start()

        #self.sync(self.secondary_database, self.primary_database)

    
    def primary_reconnect(self):
        while True:
            if self.primary_database.isOnline == False:
                try:
                    self.primary_database.test_connection.reconnect(3,0)
                except Exception as e:
                    pass
            
            time.sleep(5) #update records once every second

        
    def secondary_reconnect(self):
        while True:
            if self.secondary_database.isOnline == False:
                try:
                    self.secondary_database.test_connection.reconnect(3,0)
                except Exception as e:
                    pass
            
            time.sleep(5) #update records once every second

    
    def sync(self, source:Database, destination:Database):
        destination.needsSync = False
        print("Syncing databases")
        destination.truncateAll()
        print("trancated all")

        for table in self.table_list:
            print(f"updating table {table}")
            to_be_inserted = source.get(f"SELECT * from {table};",())
            
            if len(to_be_inserted) > 0:
                num_parameters = len(to_be_inserted[0])

                query = "INSERT INTO " + table +" VALUES (" 
                for i in range( num_parameters - 1):
                    query += "%s, "
                
                query += "%s);"
                # + "("+["%s, " for i in range (num_parameters - 1)] +"%s);"
                destination.updateMany( query, to_be_inserted)

        destination.needsSync = False
        #TODO

    def preCheck(self):
        
        # if (self.secondary_database.test_connection.is_connected()):
        #     self.secondary_database.isOnline = True
        # else:
        #     try:
        #         self.secondary_database.test_connection.reconnect(1, 0)
        #         self.secondary_database.isOnline = True
        #     except Exception as e:
        #         self.secondary_database.isOnline = False

        # if (self.primary_database.test_connection.is_connected()):
        #     self.primary_database.isOnline = True
        # else:
        #     try:
        #         self.primary_database.test_connection.reconnect(1, 0)
        #         self.primary_database.isOnline = True
        #     except Exception as e:
        #         self.primary_database.isOnline = False                

        
        self.primary_database.isOnline = self.primary_database.test_connection.is_connected()
        self.secondary_database.isOnline = self.secondary_database.test_connection.is_connected()
          
        if self.primary_database.needsSync and self.primary_database.isOnline:
            self.sync(source=self.secondary_database, destination=self.primary_database)
        if self.secondary_database.needsSync and self.secondary_database.isOnline:
            self.sync(source=self.primary_database, destination=self.secondary_database)

    def get(self,query,args):
        self.preCheck()
        reply = None

        if self.primary_database.isOnline and self.primary_database.needsSync == False:
            reply = self.primary_database.get(query,args)
            if reply:
                return reply
        if self.secondary_database.isOnline and self.secondary_database.needsSync == False:
            reply = self.secondary_database.get(query,args)
            return reply

    def update(self,query,args):
        self.preCheck()

        if self.primary_database.isOnline:
            self.primary_database.update(query,args)
        if self.secondary_database.isOnline:
            self.secondary_database.update(query,args)
    
    def updateMany(self,query,args):
        self.preCheck()

        if self.primary_database.isOnline:
            self.primary_database.updateMany(query,args)
        if self.secondary_database.isOnline:
            self.secondary_database.updateMany(query,args)