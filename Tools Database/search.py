from ast import While
from datetime import datetime
from security import get_hash

ACCOUNT = 'account'
TOOL = 'tool'
REQUEST = 'request'
CATEGORY = 'category'
BARCODE = 'barcode'
NAME = 'name'
SORT = 'sort'
RMADE = 'made'
RRECEIVED = 'received'
LIST = 'list'
AVAILABLE = 'available'
LENT = 'lent'
BORROWED = 'borrowed'


def search(curs, parameter, currUser):
    if parameter == BARCODE:
        barcode = input("input barcode: ")
        curs.execute("select * from tool where barcode = %s ORDER BY name ASC", [barcode])
        result = curs.fetchall()
        for row in result:
            print(row)
        return "", "", ""

    elif parameter == NAME:
        toolname = input("input tool name: ")
        curs.execute("select * from tool where name = %s ORDER BY name ASC", [toolname])
        result = curs.fetchall()
        for row in result:
            print(row)

        return "", "", ""

    elif parameter == CATEGORY:
        cat = input("input category name: ")

        curs.execute('select * from tool inner join organizes o on ' \
                     'tool.barcode = o.barcode where o.name = %s ORDER BY tool.name', [cat])
        result = curs.fetchall()
        for row in result:
            print(row)

        return "", "", ""

    elif parameter == SORT:
        orderby = input("input by what parameter you want to order (category or tool(name) ) : ")
        ordertype = input("input whether ASC(ascending) or DESC(descending) : ")

        if orderby == CATEGORY:

            if(ordertype.lower()=="asc"):
                curs.execute("SELECT tool.barcode, shareability,tool.name, description, "
                         "purchase_price, purchase_date, status, o.name" \
                         " FROM tool INNER JOIN organizes o on tool.barcode = o.barcode ORDER BY o.name ASC")
                result = curs.fetchall()
                #print("Ordered by tool name")
                for row in result:
                    print(row)
                
            elif(ordertype.lower()=="desc"):
                curs.execute("SELECT tool.barcode, shareability,tool.name, description, "
                         "purchase_price, purchase_date, status, o.name" \
                         " FROM tool INNER JOIN organizes o on tool.barcode = o.barcode ORDER BY o.name DESC")
                result = curs.fetchall()
                for row in result:
                    print(row)
                #return "", "", ""
            print("Ordered by CATEGORY")
            return "", "", ""


        elif orderby == TOOL:
            if ordertype.lower() == "asc":
                curs.execute("SELECT * FROM tool ORDER BY name asc")
            elif ordertype.lower() == "desc":
                curs.execute("SELECT * FROM tool ORDER BY name desc")
            else:
                print("Invalid Input")
                return "","",""
            result = curs.fetchall()
            print("Ordered by tool name")
            for row in result:
                print(row)
            return "", "", ""

    elif parameter == REQUEST:
        requestType = input("Request(s) made or received")
        if requestType == RMADE:
            curs.execute("select * from request where username = %s", [currUser])
            result = curs.fetchall()
            for row in result:
                print(row)
            return "", "", ""

        elif requestType == RRECEIVED:  # own tool + theres a request out for owned tool
            curs.execute("select * from request left join request_for rf on request.request_id = rf.request_id " \
                         "left join owns o on rf.barcode = o.barcode where o.username = %s", [currUser])

            result = curs.fetchall()
            for row in result:
                print(row)
            return "", "", ""
        else:
            print("Invalid Command")
            return "", "", ""
    elif parameter == LIST:
        listType = input("List 'available' or 'lent' or 'borrowed'?")

        if listType == AVAILABLE:
            curs.execute("select * from tool where status = 'Available' ORDER BY name", [currUser])
            result = curs.fetchall()
            for row in result:
                print(row)
            return "", "", ""

        elif listType == LENT:
            curs.execute(
                'update tool set  status = %s where barcode in (select barcode from request_for where request_id in (select request_id from request where return_date < current_date))',
                ['OVERDUE'])
            curs.execute("select *, r.username from tool join request_for rf on tool.barcode = rf.barcode join request r on rf.request_id = r.request_id where r.status = 'Accepted'")
            result = curs.fetchall()


            for row in result:
                print(row)
            return "", "", ""

        elif BORROWED:
            curs.execute('update tool set  status = %s where barcode in (select barcode from request_for where request_id in (select request_id from request where return_date < current_date))', ['OVERDUE'])

            curs.execute('select tool, o.username from tool join owns o on o.barcode = tool.barcode where tool.status = %s', ['Unavailable'])

            result = curs.fetchall()
            for row in result:
                print(row)
            return "", "", ""


def login(username, password, curs, conn):
    while True:
        hash_pw = str(get_hash(username, password))
        sql = "SELECT username, password FROM account where username= %s and password = %s"
        params = [username, hash_pw]
        curs.execute(sql, params)
        result = curs.fetchall()
        if len(result) != 1:
            print("Wrong username or password")
            username = input("Enter Username: ")
            password = input("Enter Password: ")
        else:
            date = datetime.today()
            sql = "UPDATE account SET last_accessed=%s WHERE username=%s"
            params = [date, username]
            curs.execute(sql, params)
            conn.commit()
            break

    sql = "SELECT username, password FROM account where username= %s and password = %s"
    params = [username, hash_pw]
    message = "Logged in!"
    return sql, params, message
