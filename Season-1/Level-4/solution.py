
import sqlite3
import os
from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def source():
    ops = DB_CRUD_ops()
    stock_symbol = request.args.get("input", "")

    return (
        ops.get_stock_info(stock_symbol)
        + ops.get_stock_price(stock_symbol)
    )


class Connect(object):

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
            base_path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_path, 'level-4.db')
            db_con = con.create_connection(db_path)

            if db_con is None:
                return

            cur = db_con.cursor()

            table_fetch = cur.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'stocks';
                """
            ).fetchall()

            if table_fetch == []:
                cur.execute(
                    """
                    CREATE TABLE stocks
                    (date TEXT, symbol TEXT, price REAL)
                    """
                )

                cur.execute(
                    """
                    INSERT INTO stocks VALUES (?, ?, ?)
                    """,
                    ('2022-01-06', 'MSFT', 300.00)
                )

                db_con.commit()

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            if db_con is not None:
                db_con.close()


class DB_CRUD_ops(object):

    # Retrieves all information about a stock symbol
    def get_stock_info(self, stock_symbol):

        Create()
        con = Connect()

        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_path, 'level-4.db')
            db_con = con.create_connection(db_path)

            if db_con is None:
                return None

            try:
                cur = db_con.cursor()

                res = "[METHOD EXECUTED] get_stock_info\n"

                query = "SELECT * FROM stocks WHERE symbol = ?"
                cur.execute(query, (stock_symbol,))

                query_outcome = cur.fetchall()

                for result in query_outcome:
                    res += "[RESULT] " + str(result)

                return res

            finally:
                db_con.close()

        except sqlite3.Error as e:
            print(f"ERROR: {e}")
            return None

    # Retrieves the price of a stock
    def get_stock_price(self, stock_symbol):

        Create()
        con = Connect()

        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_path, 'level-4.db')
            db_con = con.create_connection(db_path)

            if db_con is None:
                return None

            try:
                cur = db_con.cursor()

                res = "[METHOD EXECUTED] get_stock_price\n"

                query = "SELECT price FROM stocks WHERE symbol = ?"
                cur.execute(query, (stock_symbol,))

                query_outcome = cur.fetchall()

                for result in query_outcome:
                    res += "[RESULT] " + str(result) + "\n"

                return res

            finally:
                db_con.close()

        except sqlite3.Error as e:
            print(f"ERROR: {e}")
            return None

    # Updates the price of a stock
    def update_stock_price(self, stock_symbol, price):

        Create()
        con = Connect()

        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_path, 'level-4.db')
            db_con = con.create_connection(db_path)

            if db_con is None:
                return None

            try:
                cur = db_con.cursor()

                if not isinstance(price, float):
                    raise ValueError(
                        "ERROR: stock price provided is not a float"
                    )

                res = "[METHOD EXECUTED] update_stock_price\n"

                query = "UPDATE stocks SET price = ? WHERE symbol = ?"
                cur.execute(query, (price, stock_symbol))

                db_con.commit()

                return res

            finally:
                db_con.close()

        except (sqlite3.Error, ValueError) as e:
            print(f"ERROR: {e}")
            return None
