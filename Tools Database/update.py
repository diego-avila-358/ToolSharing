from datetime import datetime, timedelta

ACCOUNT = 'account'
TOOL = 'tool'
REQUEST = 'request'
CATEGORY = 'category'

current_user = ''

def update(entity, curs):
    if entity == CATEGORY:
        barcode = input("Enter barcode of tool: ")
        name = input("Enter category name you want to add tool into: ")
        curs.execute("select name from categories where name = %s", [name])
        result = curs.fetchall()

        if(len(result)==0):
            print("category does not exists")

        sql = "update organizes set name = %s where barcode = %s"
        params = [name, barcode]
        message = "Tool added into category!"
        return sql, params, message
    elif entity == TOOL:
        barcode = input("Enter barcode of tool: ")
        change = input("What would you like to change? (shareability, name, description) ")
        if change == 'shareability':
            share = input("Will this tool be shareable? (y/n)")

            if share == 'n':
                update = 'Not Shareable'

            elif share == 'y':
                update = 'Shareable'

            sql = "update tool set shareability = %s where barcode=%s"

            params = [update, barcode]
            message = "Tool changed!"
            return sql, params, message

        elif change == 'name':
            update = input("Enter Tool Name: ")
            sql = "update tool set name = %s where barcode=%s"

            params = [update, barcode]
            message = "Tool changed!"
            return sql, params, message

        elif change == 'description':
            update = input("Enter tool description: ")
            sql = "update tool set description = %s where barcode=%s"
            params = [update, barcode]
            message = "Tool changed!"
            return sql, params, message
        else:
            print("No change made.")
            return
        #sql = "update tool set shareability = %s where barcode=%s"
    elif entity == REQUEST:
        received = input("Do you want to update a request you received? (y/n) ")
        request_id = input("What is the request id of the request you want to change? ")
        change = ''
        update = ''
        if received == 'y':
            change += input("What would you like to change? (duration or status)")
            if change == 'duration':
                update += input("Enter duration: ")
            elif change == 'status':
                update += input("Change status to Accepted? (y/n)")
                if update == 'y':
                    update = 'Accepted'

                else:
                    update = 'Denied'
            else:
                print("No change made.")
                return "","",""
        else:
            change += input("What would you like to change? (date_needed, duration, tool)")
            if change == 'date_needed':
                update += input("Enter date needed (YYYY-MM-DD): ")
            elif change == 'duration':
                update += input("Enter duration: ")
            elif change == 'tool':
                update += input("Enter the barcode of the tool you want to borrow: ")
            else:
                print("No change made.")
                return "", "", ""
        sql = ''
        params = []
        if change == 'tool':
            sql += 'update request_for set barcode=%s where request_id=%s'
            params += update, request_id
        elif change == 'status':
            if update == 'Accepted':
                curs.execute('select barcode from tool where barcode in '
                             '(select barcode from request_for where request_id=%s) '
                             'and shareability=\'Shareable\'', [request_id])
                result = curs.fetchall()
                if len(result) == 0:
                    print("No change made.")
                    return
            sql += 'update request set status=%s where request_id=%s'
            params += [update, request_id]
            print("Status changed!")
        elif change == 'date_needed':
            curs.execute('select date_needed from request where request_id=%s', [request_id])
            result = curs.fetchone()[0]
            print(result)
            print(update)

            return_date = datetime.fromisoformat(update)

            sql += 'update request set date_needed=%s where request_id=%s'
            params += [return_date, request_id]
        else:
            sql += 'update request set %s=%s where request_id=%s'
            params += [change, update, request_id]


        message = 'Request Updated!'
        return sql, params, message
    elif entity == 'borrowed':
        curs.execute('select tool.barcode from tool inner join request_for rf on tool.barcode = rf.barcode '
                     'inner join request r on rf.request_id = r.request_id inner join account a on '
                     'a.username = r.username where tool.status=\'Unavailable\' and r.status =\'Accepted\' '
                     'and r.username = %s and shareability = \'Shareable\'', [current_user])
        result = curs.fetchall()
        if len(result) > 0:
            sql = 'update tool set status=Available where barcode=%s; ' \
                  'update request set return_date = current_date where request_id in ' \
                  '(select request_id from request_for where barcode = %s))'
            params = [result, result]
            message = 'Status of borrowed tool updated!'
            return sql, params, message
        print('You have no borrowed tools.')
        return '', [], ''
