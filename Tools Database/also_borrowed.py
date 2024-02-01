import random
from datetime import datetime, timedelta


def recommendation(curs, toolUser, barcode, conn):
    """
    :param barcode:
    :param curs:
    """
    sql = "select name, barcode from tool where barcode in (select barcode from request_for where request_id in " \
          "(select request_id from request where username in (select username from request where request_id in " \
          "(select request_id from request_for where barcode = %s))) group by barcode order by count(barcode) " \
          "desc limit 4) and %s != barcode;"
    params = [barcode, barcode]
    curs.execute(sql, params)
    message = "Request created!"
    print(message)
    print("Would you like to borrow these tools users have also borrowed?")
    result = curs.fetchall()
    i = 1
    for row in result:
        print(i, ':', row)
        i += 1
    user = input("(y or n) ")
    if user == 'y':
        tool_num = input("Enter number of the tool needed: ")
        barcode_other = ''
        if tool_num == '1':
            for row in result:
                r = str(row)
                ra = r.split(',')
                barcode_other = ra[1].strip(')')
                break
        elif tool_num == '2':
            i = 1
            for row in result:
                if i == 2:
                    r = str(row)
                    ra = r.split(',')
                    barcode_other = ra[1].strip(')')
                    break
                i += 1
        elif tool_num == '3':
            i = 1
            for row in result:
                if i == 3:
                    r = str(row)
                    ra = r.split(',')
                    barcode_other = ra[1].strip(')')
                    break
                i += 1
        result = ["a"]
        request_id = 0
        while len(result) > 0:
            request_id = random.randint(000000, 999999)
            curs.execute("Select request_id from request_for where request_id = %s ", [request_id])
            result = curs.fetchall()
        status = "Pending"
        date_needed = input("When do you need the tool by? (YYYY-MM-DD) ")
        date = datetime.fromisoformat(date_needed)
        duration = input("How many days do you need it for? ")
        return_date = date.__add__(timedelta(days=float(duration)))
        barcode = barcode_other
        curs.execute("Select name from tool where barcode = %s and status='Available'", [barcode])
        result = curs.fetchall()
        while len(result) <= 0:
            barcode = input("You inputted a barcode of a tool that is either unavailable or doesn't exist. What is "
                            "the barcode of the tool you want to borrow? ")
            curs.execute("Select name from tool where barcode = %s and status=Available", [barcode])
            result = curs.fetchall()
        sql = "insert into request values(%s, %s, %s, %s, %s, %s); insert into request_for values(%s, %s)"
        params = [request_id, toolUser, status, date, duration, return_date, request_id, barcode]
        curs.execute(sql, params)
        conn.commit()
    else:
        return
