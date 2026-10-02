import os

import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the project folder

# HTTP-style status codes for common MySQL connection errors; anything else is reported as 500.
STATUS_CODES = {
    errorcode.ER_ACCESS_DENIED_ERROR: (401, "Wrong username or password"),
    errorcode.ER_DBACCESS_DENIED_ERROR: (403, "User isn't allowed to use this database"),
    errorcode.ER_BAD_DB_ERROR: (404, "Database not found"),
    errorcode.CR_UNKNOWN_HOST: (404, "Database host not found"),
    errorcode.CR_CONN_HOST_ERROR: (503, "Database server is unreachable"),
    errorcode.CR_CONNECTION_ERROR: (503, "Database server is unreachable"),
    errorcode.CR_SERVER_LOST: (504, "Database server timed out"),
    errorcode.CR_SSL_CONNECTION_ERROR: (495, "SSL certificate problem (check DB_SSL_CA / ca.pem)"),
}


def get_connection():
    """Open a connection to the cloud-hosted MySQL database described in .env."""
    settings = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "connection_timeout": 10,  # fail fast instead of hanging if the cloud host is unreachable
    }
    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca:  # hosted databases such as Aiven need an encrypted connection
        if not os.path.isfile(ssl_ca):
            print(f"[404] SSL certificate file not found: {ssl_ca}")
            return None
        settings["ssl_ca"] = ssl_ca
        settings["ssl_verify_cert"] = True
    try:
        cnx = mysql.connector.connect(**settings)
    except mysql.connector.Error as err:
        code, reason = STATUS_CODES.get(err.errno, (500, "Unexpected database error"))
        print(f"[{code}] {reason}: {err.msg}")
        return None
    print("[200] Connected to the database")
    return cnx


if __name__ == "__main__":  # running db.py directly just tests the connection
    connection = get_connection()
    if connection is not None:
        connection.close()
