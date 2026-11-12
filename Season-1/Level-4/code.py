'''
Please note:

The first file that you should run in this level is tests.py for database creation, with all tests passing.
Remember that running the hack.py will change the state of the database, causing some tests inside tests.py
to fail.

If you like to return to the initial state of the database, please delete the database (level-4.db) and run 
the tests.py again to recreate it.

SECURE VERSION: every query is executed with bound parameters (or, for the free-form methods,
restricted to single read-only SELECT statements). The "[QUERY]" lines are only log text and
keep the original format so the existing tests keep passing; they are never what gets executed.
'''

import re
import sqlite3
import os
from flask import Flask, request

# only short uppercase ticker symbols are accepted at the web layer (defense in depth,
# NOT a replacement for parameterized queries)
SYMBOL_PATTERN = re.compile(r"^[A-Z]{1,5}$")

### Web layer
app = Flask(__name__)


@app.route("/")
def source():
    symbol = request.args.get("input", "")
    if not SYMBOL_PATTERN.match(symbol):
        return "Invalid stock symbol", 400

    ops = DB_CRUD_ops()
    res = (ops.get_stock_info(symbol) or "") + "\n"
    res += ops.get_stock_price(symbol) or ""
    return res, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/update")
def update():
    symbol = request.args.get("input", "")
    if not SYMBOL_PATTERN.match(symbol):
        return "Invalid stock symbol", 400
    try:
        price = float(request.args.get("price", ""))
    except ValueError:
        return "Invalid price", 400

    res = DB_CRUD_ops().update_stock_price(symbol, price) or ""
    return res, 200, {"Content-Type": "text/plain; charset=utf-8"}


class Connect(object):

    # helper function creating database with the connection
    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
        except sqlite3.Error as e:
            print(f"ERROR: {e}")
        return connection


class Create(object):

    def __init__(self):
        con = Connect()
        db_con = None
        try:
            # creates a dummy database inside the folder of this challenge
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            # checks if tables already exist, which will happen when re-running code
            table_fetch = cur.execute(
                '''
                SELECT name 
                FROM sqlite_master 
                WHERE type='table'AND name='stocks';
                ''').fetchall()

            # if tables do not exist, create them and insert dummy data
            if table_fetch == []:
                cur.execute(
                    '''
                    CREATE TABLE stocks
                    (date text, symbol text, price real)
                    ''')

                # inserts dummy data to the 'stocks' table, representing average price on date
                cur.execute(
                    "INSERT INTO stocks VALUES ('2022-01-06', 'MSFT', 300.00)")
                db_con.commit()

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()


class DB_CRUD_ops(object):

    # opens a connection to the database, creating it first if needed.
    # read-only connections cannot modify data even if a bug lets something slip through.
    def _connect(self, read_only=False):
        # building database from scratch as it is more suitable for the purpose of the lab
        Create()
        path = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(path, 'level-4.db')
        if read_only:
            return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        return sqlite3.connect(db_path)

    # a free-form statement is only accepted if it is a single SELECT
    @staticmethod
    def _is_select(statement):
        return re.match(r"^\s*SELECT\b", statement, re.IGNORECASE) is not None

    # retrieves all info about a stock symbol from the stocks table
    # Example: get_stock_info('MSFT') will result into executing
    # SELECT * FROM stocks WHERE symbol = 'MSFT'
    def get_stock_info(self, stock_symbol):
        db_con = None
        try:
            db_con = self._connect(read_only=True)
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] get_stock_info\n"
            # log text only: this string is never executed
            query = "SELECT * FROM stocks WHERE symbol = '{0}'".format(stock_symbol)
            res += "[QUERY] " + query + "\n"

            # extra layer kept from the original: reject suspicious-looking input.
            # This is defense in depth; the parameterized query below is the real protection.
            restricted_chars = ";%&^!#-"
            has_restricted_char = any([char in query for char in restricted_chars])
            correct_number_of_single_quotes = query.count("'") == 2

            if has_restricted_char or not correct_number_of_single_quotes:
                res += "CONFIRM THAT THE ABOVE QUERY IS NOT MALICIOUS TO EXECUTE"
            else:
                # the symbol is bound as data, so it can never change the structure of the query
                cur.execute("SELECT * FROM stocks WHERE symbol = ?", (stock_symbol,))

                query_outcome = cur.fetchall()
                for result in query_outcome:
                    res += "[RESULT] " + str(result)
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()

    # retrieves the price of a stock symbol from the stocks table
    # Example: get_stock_price('MSFT') will result into executing
    # SELECT price FROM stocks WHERE symbol = 'MSFT'
    def get_stock_price(self, stock_symbol):
        db_con = None
        try:
            db_con = self._connect(read_only=True)
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] get_stock_price\n"
            # log text only: this string is never executed
            query = "SELECT price FROM stocks WHERE symbol = '" + stock_symbol + "'"
            res += "[QUERY] " + query + "\n"

            # execute() (never executescript()) refuses multiple statements, blocking stacked queries
            cur.execute("SELECT price FROM stocks WHERE symbol = ?", (stock_symbol,))
            query_outcome = cur.fetchall()
            for result in query_outcome:
                res += "[RESULT] " + str(result) + "\n"
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()

    # updates stock price
    def update_stock_price(self, stock_symbol, price):
        db_con = None
        try:
            if not isinstance(price, float):
                raise Exception("ERROR: stock price provided is not a float")

            db_con = self._connect()
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] update_stock_price\n"
            # UPDATE stocks SET price = 310.0 WHERE symbol = 'MSFT'
            # log text only (same format the tests expect): the real update uses bound parameters
            query = "UPDATE stocks SET price = '%d' WHERE symbol = '%s'" % (price, stock_symbol)
            res += "[QUERY] " + query + "\n"

            # binding the float keeps its full value (the original '%d' truncated 310.75 to 310)
            cur.execute("UPDATE stocks SET price = ? WHERE symbol = ?", (price, stock_symbol))
            db_con.commit()
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()

    # executes multiple queries, but only SELECT statements, one at a time, on a read-only connection
    # Example: SELECT price FROM stocks WHERE symbol = 'MSFT';
    #          SELECT * FROM stocks WHERE symbol = 'MSFT'
    def exec_multi_query(self, query):
        db_con = None
        try:
            db_con = self._connect(read_only=True)
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] exec_multi_query\n"
            for query in filter(None, query.split(';')):
                res += "[QUERY]" + query + "\n"
                query = query.strip()
                if not self._is_select(query):
                    res += "[BLOCKED] only SELECT statements are allowed\n"
                    continue
                cur.execute(query)

                query_outcome = cur.fetchall()
                for result in query_outcome:
                    res += "[RESULT] " + str(result) + " "
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()

    # executes SELECT queries given by the user in the form of a script.
    # executescript() is never used, and the connection is read-only.
    # Example: SELECT price FROM stocks WHERE symbol = 'MSFT';
    #          SELECT * FROM stocks WHERE symbol = 'MSFT'
    def exec_user_script(self, query):
        db_con = None
        try:
            db_con = self._connect(read_only=True)
            cur = db_con.cursor()

            res = "[METHOD EXECUTED] exec_user_script\n"
            res += "[QUERY] " + query + "\n"
            for statement in filter(None, (s.strip() for s in query.split(';'))):
                if not self._is_select(statement):
                    res += "[BLOCKED] only SELECT statements are allowed\n"
                    continue
                cur.execute(statement)
                query_outcome = cur.fetchall()
                for result in query_outcome:
                    res += "[RESULT] " + str(result)
            return res

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con:
                db_con.close()