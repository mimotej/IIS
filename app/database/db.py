import mysql.connector
from mysql.connector import Error
import logging as logger
logger.basicConfig(level=logger.DEBUG)

class SQLConn:

    def __init__(self, host='127.0.0.1', database='IIS', user='root', password='IISkokos1999?'):
        try:
            self.__connection = mysql.connector.connect(host=host,
                                                 database=database,
                                                 user=user,
                                                 password=password)
            if self.__connection.is_connected():
                logger.debug("Connected to MySQL Server version " + self.__connection.get_server_info())
                self.__cursor = self.__connection.cursor()
                self.__cursor.execute("select database();")
                print("You're connected to database: ", self.__cursor.fetchone())

        except Error as e:
            logger("Error while connecting to MySQL", e)
    
    def __del__(self):
        if (self.__connection.is_connected()):
            self.__cursor.close()
            self.__connection.close()
            logger.debug("MySQL connection is closed")

    def select(self, statement):
        self.__cursor.execute(statement)
        return self.__cursor.fetchall()