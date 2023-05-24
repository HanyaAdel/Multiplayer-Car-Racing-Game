import mysql.connector.pooling
import os
import string
import random
from dotenv import load_dotenv

load_dotenv()

SESSION_CODE_SIZE = 5

class Model:

    def __init__(self) -> None:
        self.connection_pool = self.create_connection_pool()

    def create_connection_pool(self):
        db_config = {
            "host":os.getenv('DB_HOST'),
            "user":os.getenv('DB_USER'),
            'password':os.getenv('DB_PASSWD'),
            'database':os.getenv('DB_DATABASE')
        }
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "mypool",
            pool_size = 5,
            autocommit = True,
            **db_config
        )
        return connection_pool

    def get_Connection(self):
        return self.connection_pool.get_connection()

    def login(self,username, password):
        db = self.get_Connection()
        mycursor = db.cursor()
        query = "SELECT * FROM player where username=%s AND password=%s;"
        mycursor.execute(query,(username,password,))

        result = mycursor.fetchone()
        db.close()
        if mycursor.rowcount == 1:
            return result[0]
        return None
    
    def generateSessionCode(self):
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = SESSION_CODE_SIZE))
        return ran
    
    def getSessionCodes(self):
        db = self.get_Connection()
        mycursor = db.cursor()
        query = "SELECT code FROM session;"
        mycursor.execute(query)
        result=mycursor.fetchall()
        db.close()
        return result

    def addSession(self):
        session_codes = self.getSessionCodes()
        while True:
            session_code = self.generateSessionCode()
            if session_code in session_codes:
                continue
            db = self.get_Connection()
            mycursor = db.cursor()
            query = "INSERT INTO session (code) VALUES (%s);"
            mycursor.execute(query,(session_code,))
            db.commit()
            db.close()
            return session_code
        
    def deleteSession(self, session_code):
        db = self.get_Connection()
        mycursor = db.cursor()
        query = "DELETE FROM session WHERE (`code` = %s);"
        mycursor.execute(query,(session_code,))
        db.commit()
        db.close()

    def getPlayerScore(self,player_id,session_code):
        db = self.get_Connection()
        mycursor = db.cursor()
        query = "SELECT score FROM player_in_session where id_player = %s AND code_session = %s;"
        mycursor.execute(query, (player_id, session_code,))
        result = mycursor.fetchone()
        db.close()
        if mycursor.rowcount == 1:
            return result[0]
        return None

    def addPlayerToSession(self, player_id, session_code):
        score = self.getPlayerScore(player_id=player_id, session_code=session_code)
        if score:
            return score
        db = self.get_Connection()
        mycursor = db.cursor()
        query = "INSERT INTO player_in_session (id_player,code_session,score) VALUES (%s,%s,%s);"
        mycursor.execute(query,(player_id,session_code,0,))
        db.commit()
        db.close()
        return 0

    
    def updateRecords(self, players_list):
        db = self.get_Connection()
        mycursor = db.cursor()
        query = "UPDATE player_in_session SET score=%s WHERE id_player=%s AND code_session=%s;"
        mycursor.executemany(query,players_list)
        db.commit()
        db.close()

    def printStuff(self):
        print("printing from")

