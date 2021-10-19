import sys
from psycopg2 import connect
from configparser import ConfigParser
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError, errorcodes, errors

# Reading database credentials from config.txt
config = ConfigParser()
config.read("config.txt")
# print(dict(config.items("PG")))

# function that handles and parses psycopg2 exceptions
def print_psycopg2_exception(err):
    # details_exception
    err_type, err_obj, traceback = sys.exc_info()
    line_num = traceback.tb_lineno
    # the connect() error
    print("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print("psycopg2 traceback:", traceback, "-- type:", err_type)
    # psycopg2 extensions.Diagnostics object attribute
    print("\nextensions.Diagnostics:", err.diag)
    # pgcode and pgerror exceptions
    print("pgerror:", err.pgerror)
    print("pgcode:", err.pgcode, "\n")
    raise err
class Database:

    # Database class constructor
    def __init__(self, db_params):
        self.db_params = db_params
        print('Database class object created...')
    # Database class instance method

    def connect(self):
        try:
            self.conn = connect(**self.db_params)
            self.cur = self.conn.cursor(cursor_factory=DictCursor)
            print('Database connection has been Successful...')
        except OperationalError as err:
            # pass exception to function
            print_psycopg2_exception(err)
            # set the connection to 'None' in case of error
            self.conn = None

    def executequery(self, query):
        # Check if the connection was successful
        try:
            if self.conn != None: 
                self.cursor = self.conn.cursor()
                print("cursor object:", self.cursor, "\n")
                # catch exception for invalid SQL statement
                try:
                    self.cursor.execute(query)
                    try:
                        result = self.cursor.fetchall()
                        # print(result)
                        return result
                    except:
                        return self.cursor.statusmessage
                except Exception as err:
                    print_psycopg2_exception(err)
                    # rollback the previous transaction before starting another
                    self.conn.rollback()
                # closing  cursor object to avoid memory leaks
                # cursor.close()
                # self.conn.close()
            else:
                print("Database is not connected")
        except Exception as err :
            print("Oops ! You forget to have connection first")
            raise err
        
        #function for clossing connection to avoid memory leaks
    def close_conn(self):
        # Check if the connection was successful
        try:
            if self.conn != None: 
                if self.cursor:
                    self.cursor.close()
                    self.conn.close()
                    print("Connection closed")
        except Exception as err :
            raise err
class Mapathon:
    #constructor
    def __init__(self):
        self.obj1 = Database(dict(config.items("PG")))
        self.obj1.connect()
        print('Mapathon class object also created...')

    # Mapathon class instance method
    def getall_validation(self):
        query = f"""
            SELECT *
            FROM validation           
            """
        # calling executequery() method of Database class
        self.obj1.executequery(query)
        print('Mapathon class getall_validation() method executed...')
