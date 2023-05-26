from database import Database

class DatabaseManager:
    def __init__(self) -> None:
        self.primary_database = Database(isPrimary=True)
        self.secondary_database = Database(isPrimary=False)

    def sync(self, source:Database, destination:Database):
        print("Syncing databases")
        destination.needsSync = False
        #TODO

    def preCheck(self):
        if self.primary_database.needsSync and self.primary_database.isOnline:
            self.sync(source=self.secondary_database, destination=self.primary_database)
        if self.secondary_database.needsSync and self.secondary_database.isOnline:
            self.sync(source=self.primary_database, destination=self.secondary_database)

    def get(self,query,args):
        self.preCheck()
        reply = None
        reply = self.primary_database.get(query,args)
        if reply:
            return reply
        reply = self.secondary_database.get(query,args)
        return reply

    def update(self,query,args):
        self.preCheck()
        self.primary_database.update(query,args)
        self.secondary_database.update(query,args)
    
    def updateMany(self,query,args):
        self.preCheck()
        self.primary_database.updateMany(query,args)
        self.secondary_database.updateMany(query,args)