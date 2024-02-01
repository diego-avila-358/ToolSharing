import random
from datetime import datetime, timedelta

from also_borrowed import recommendation
from security import get_hash

ACCOUNT = 'account'
TOOL = 'tool'
REQUEST = 'request'
CATEGORY = 'category'

curr_user = ""


def set_user(username):
    create.curr_user = username
    return


def create(entity, curs, toolUser, conn):
    if entity == ACCOUNT:
        while True:
            u = input("Enter Username: ")
            curs.execute("select username from account where username = %s", [u])
            result = curs.fetchall()
            if len(result) == 0:
                username = u
                break
            else:
                print("Username", u, "is already taken try again!")

        password = input("Enter Password: ")

        hash_password = str(get_hash(username, password))

        name = input("Enter Name (last, first): ")
        name = name.split(',')
        if len(name) > 1:
            first_name = name[1].strip()
            last_name = name[0].strip()
        else:
            # change this to re-prompt the user
            first_name = "first_error"
            last_name = "last_error"
        email = input("Enter Email: ")
        last_accessed = datetime.today()
        creation_date = datetime.today()
        sql = "insert into account values(%s, %s, %s, %s, %s, %s, %s) returning username"
        params = [username, hash_password, first_name, last_name, email, last_accessed, creation_date]
        message = "Account created!"
        return sql, params, message

    elif entity == TOOL:
        name = input("Enter Tool Name: ")
        share = input("Will this tool be shareable? (y/n)")
        if share == 'n':
            shareability = 'Not Shareable'
        else:
            shareability = 'Shareable'
        description = input("Enter Tool Description: (Press Enter to Skip) ")
        purchase_price = None
        pp = input("Enter Purchase Price: (Press Enter to Skip) ")
        if pp != "":
            purchase_price = int(pp)
        p_date = input("Enter Purchase Date (YYYY-MM-DD): (Press Enter to Skip) ")
        set_user(toolUser)
        if p_date == "":
            purchase_date = None
        else:
            purchase_date = datetime.fromisoformat(p_date)
        result = ["a"]
        barcode = 0
        while len(result) > 0:
            barcode = random.randint(000000, 999999)
            curs.execute("Select barcode from tool where barcode = %s ",
                         [barcode])  # second param is auto as a list; change the barcode
            result = curs.fetchall()
        category = input("Enter Category: ")
        status = 'Available' if share == 'y' else 'Unavailable'
        if purchase_date and len(description) > 0:
            sql = "insert into tool values(%s, %s, %s, %s, %s, %s, %s);" \
                  "insert into owns values(%s, %s);" \
                  "insert into organizes values(%s, %s)"
            params = [barcode, shareability, name, description, purchase_price, purchase_date, status,
                      toolUser, barcode, barcode, category]
            message = "Tool created!"
            return sql, params, message
        elif (purchase_date is None) and len(description) > 0:
            sql = "insert into tool values(%s, %s, %s, %s, %s, %s, %s);" \
                  "insert into owns values(%s, %s);" \
                  "insert into organizes values(%s, %s)"
            params = [barcode, shareability, name, description, purchase_price, None, status,
                      toolUser, barcode, barcode, category]
            message = "Tool created!"
            return sql, params, message
        elif (purchase_date is None) and description == "":
            sql = "insert into tool values(%s, %s, %s, %s, %s, %s, %s);" \
                  "insert into owns values(%s, %s);" \
                  "insert into organizes values(%s, %s)"
            params = [barcode, shareability, name, '', purchase_price, None, status,
                      toolUser, barcode, barcode, category]
            message = "Tool created!"
            return sql, params, message

    elif entity == REQUEST:
        result = ["a"]
        request_id = 0
        while len(result) > 0:
            request_id = random.randint(000000, 999999)
            curs.execute("Select request_id from request_for where request_id = %s ", [request_id])
            result = curs.fetchall()
        set_user(toolUser)
        status = "Pending"
        date_needed = input("When do you need the tool by? (YYYY-MM-DD) ")
        date = datetime.fromisoformat(date_needed)
        duration = input("How many days do you need it for? ")
        return_date = date.__add__(timedelta(days=float(duration)))
        barcode = input("What is the barcode of the tool you want to borrow? ")
        curs.execute("Select name from tool where barcode = %s and status='Available'", [barcode])
        result = curs.fetchall()
        while len(result) <= 0:
            barcode = input("You inputted a barcode of a tool that is either unavailable or doesn't exist. What is "
                            "the barcode of the tool you want to borrow? ")
            curs.execute("Select name from tool where barcode = %s and status=Available", [barcode])
            result = curs.fetchall()
        sql = "insert into request values(%s, %s, %s, %s, %s, %s); insert into request_for values(%s, %s)"
        params = [request_id, toolUser, status, date, duration, return_date, request_id, barcode]
        message = "Request created!"
        recommendation(curs, toolUser, barcode, conn)
        return sql, params, message

    elif entity == CATEGORY:
        name = input("Enter Category Name: ")
        sql = "insert into categories values(%s)"
        params = [name]
        message = "Category created!"
        return sql, params, message
