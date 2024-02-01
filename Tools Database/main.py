import io

import psycopg2
from sshtunnel import SSHTunnelForwarder

import search
import getpass
from create import *
from delete import delete
from search import *
from update import update
from top_ten import top_borrowed, top_lent

USERNAME = input('Username: ')
PASSWORD = getpass.getpass()

DB_NAME = "p32002_33"

ACCOUNT = 'account'
TOOL = 'tool'
REQUEST = 'request'
CATEGORY = 'category'


def get_access(curs, conn):
    print("==== Commands: 'create account' or 'login' ====")
    i = input('Enter command: ')
    tok = i.split()
    while True:
        if tok[0] == 'h' or tok[0] == 'help':
            print()
        elif tok[0] == 'create':
            return create(tok[1], curs, curr_user, conn)

        # need search function to check access

        elif tok[0] == 'login':
            username = input("Enter Username: ")
            password = input("Enter Password: ")
            return login(username, password, curs, conn)


def display(curs, currUser):
    # number of tools available from users catalog
    curs.execute("select count(barcode) from tool where status = 'Available' and barcode in "
                 "(select barcode from owns where username=%s)", [currUser])
    result = curs.fetchall()[0]
    print(result[0], 'of your tool(s) are available.')
    # number of tools available from catalog
    curs.execute("select count(barcode) from tool where status = 'Available'")
    result = curs.fetchall()[0]
    print(result[0], ' tool(s) are available.')
    # number of tools you have lent out
    curs.execute("select count(tool.barcode) from tool join owns o on tool.barcode = o.barcode where o.username=%s and "
                 "tool.status='Unavailable' or tool.status='OVERDUE' and tool.shareability='Shareable'", [currUser])
    result = curs.fetchall()[0]
    print(result[0], 'of your tool(s) are lent out.')
    # number of lent tools
    curs.execute("select count(tool.barcode) from tool join request_for rf on tool.barcode = rf.barcode join request r "
                 "on rf.request_id = r.request_id where r.status = 'Accepted'")
    result = curs.fetchall()[0]
    print(result[0], 'tool(s) are lent out.')
    # number of tools you have borrowed
    curs.execute("select count(tool.barcode) from tool join request_for rf on tool.barcode = rf.barcode join request r "
                 "on rf.request_id = r.request_id where r.username=%s and r.status='Accepted' and "
                 "tool.status='Unavailable'", [currUser])
    result = curs.fetchall()[0]
    print(result[0], 'tool(s) are currently being borrowed by you.')
    # number of borrowed tools
    curs.execute("select count(tool.barcode) from tool join owns o on o.barcode = tool.barcode where "
                 "tool.status = 'Unavailable' or tool.status = 'OVERDUE'")
    result = curs.fetchall()[0]
    print(result[0], 'tool(s) are currently being borrowed.')
    return


def get_commands(curs, username, conn):
    display(curs, username)
    print("==== Commands: 'create' or 'delete' or 'update' or 'search' or 'list' or 'sort' ====")
    i = input('Enter command: ')
    tok = i.split()
    while True:
        if tok[0] == 'h' or tok[0] == 'help':
            print("Available commands: ")
            print("> create")
            print("> delete")
            print("> update")
            print("> search")
            print("> list")
            print("> sort")
            i = input('Enter command: ')
            tok = i.split()
        elif tok[0] == 'create':
            i = input('What entity would you like to create? (tool, category, request) ')
            if i == REQUEST:
                set_user(username)
                return create(i, curs, username, conn)
            elif i == TOOL:
                set_user(username)
                return create(i, curs, username, conn)
            elif i == CATEGORY:
                set_user(username)
                return create(i, curs, username, conn)

        elif tok[0] == 'delete':
            i = input('What entity would you like to delete? (tool, category, request) ')
            return delete(i, curs)
        elif tok[0] == 'update':
            i = input('What entity would you like to update? (borrowed, tool, category, request) ')
            update.current_user = username
            return update(i, curs)
        elif tok[0] == 'sort' or tok[0] == 'list':
            search.currUser = username
            return search(curs, tok[0], username)
        elif tok[0] == 'search':
            search.currUser = username

            i = input('What entity would you like to search? (name, category, sort, barcode, request, list) ')
            return search(curs, i, username)
        else:
            return None


def main():
    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=USERNAME,
                                ssh_password=PASSWORD,
                                remote_bind_address=('localhost', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'database': DB_NAME,
                'user': USERNAME,
                'password': PASSWORD,
                'host': 'localhost',
                'port': server.local_bind_port
            }
            conn = psycopg2.connect(**params)
            curs = conn.cursor()



            print("Database connection established\n")
            print("Welcome! LOGIN or CREATE ACCOUNT to get started.")

            # access or create account
            sql, params, message = get_access(curs, conn)
            if sql != "":
                curs.execute(sql, params)
            curr_user = curs.fetchone()[0]
            print("Welcome", curr_user)

            top_borrowed(curs)
            top_lent(curs)

            conn.commit()
            print(message)
            while True and (sql is not None):
                sql, params, message = get_commands(curs, curr_user, conn)
                if sql != "":
                    curs.execute(sql, params)
                    print(message)
                    conn.commit()

    except Exception as ex:
        print("Connection failed", ex)
    finally:
        if conn is not None:
            curs.close()
            conn.close()


if __name__ == '__main__':
    main()
