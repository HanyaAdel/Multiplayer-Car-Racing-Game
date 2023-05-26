import string
import random
from databaseManager import DatabaseManager

SESSION_CODE_SIZE = 5

class Model:

    def __init__(self) -> None:
        self.database_manager = DatabaseManager()

    def login(self,username, password):
        query = "SELECT * FROM player where username=%s AND password=%s;"
        result = self.database_manager.get(query=query,args=(username,password,))
        if len(result):
            return result[0][0]
        return None
        
    def generateSessionCode(self):
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = SESSION_CODE_SIZE))
        return ran
    
    def getSessionCodes(self):
        query = "SELECT code FROM session;"
        result = self.database_manager.get(query=query,args=())
        print("get session codes result",list(sum(result, ())))
        return list(sum(result, ()))

    def addSession(self):
        session_codes = self.getSessionCodes()
        while True:
            session_code = self.generateSessionCode()
            if session_code in session_codes:
                continue
            query = "INSERT INTO session (code) VALUES (%s);"
            self.database_manager.update(query=query,args=(session_code,))
            return session_code
        
    def deleteSession(self, session_code):
        query = "DELETE FROM session WHERE (`code` = %s);"
        self.database_manager.update(query=query,args=(session_code,))

    def getPlayerScore(self,player_id,session_code):
        query = "SELECT score FROM player_in_session where id_player = %s AND code_session = %s;"
        result = self.database_manager.get(query=query,args=(player_id, session_code,))
        if len(result):
            print("get player score result", result[0][0])
            return result[0][0]
        return None
    
    def getSessionMessages(self, session_code):
        query = "SELECT id_player , message FROM message_in_session where code_session = %s;"
        result = self.database_manager.get(query=query,args=(session_code,))
        return result

    def addPlayerToSession(self, player_id, session_code):
        score = self.getPlayerScore(player_id=player_id, session_code=session_code)
        if score:
            return score
        query = "INSERT INTO player_in_session (id_player,code_session,score) VALUES (%s,%s,%s);"
        self.database_manager.update(query=query,args=(player_id,session_code,0,))
        return 0

    def updateRecords(self, players_list):
        query = "UPDATE player_in_session SET score=%s WHERE id_player=%s AND code_session=%s;"
        self.database_manager.updateMany(query=query, args=players_list)
    
    def addMessage(self, player_id, session_code, message):
        query = "INSERT INTO message_in_session (id_player,code_session,message) VALUES (%s,%s,%s);"
        self.database_manager.update(query=query,args=(player_id,session_code,message,))

    def printStuff(self):
        print("printing from")

