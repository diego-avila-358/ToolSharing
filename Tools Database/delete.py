ACCOUNT = 'account'
TOOL = 'tool'
REQUEST = 'request'
CATEGORY = 'category'


def delete(entity, curs):
    # Deleting account is unnecessary
    if entity == ACCOUNT:
        name = input("Enter Account Username: ")
        sql = "delete from account where username=%s"
        params = [name]
        message = "Account deleted!"
        return sql, params, message

    elif entity == TOOL:
        barcode = input("Enter Tool Barcode: ")

        curs.execute("select request_id from request_for where barcode = %s", [barcode])
        result = curs.fetchall()

        # if there is no request for tool then just delete
        if len(result) == 0:
            curs.execute("delete from organizes where barcode = %s;", [barcode])
            curs.execute("delete from owns where barcode = %s;", [barcode])
        # Delete request out for
        else:
            curs.execute("delete from organizes where barcode = %s;", [barcode])
            curs.execute("delete from owns where barcode = %s;", [barcode])
            curs.execute("select barcode from tool where barcode=%s AND status='Available'", [barcode])
            av_result = curs.fetchall()

            #Check there is no request out for the tool
            if len(av_result) != 0:
                curs.execute("delete from request_for where barcode = %s;", [barcode])
                curs.execute("delete from request where request_id = %s", [result[0]])
            #Don't delete if the tool is unavailable
            else:
                print("That tool is currently being borrowed.")

                return "", "", ""

        # This statement should be nothing if the request is active
        sql = "delete from organizes where barcode = %s;" \
              "delete from owns where barcode = %s;" \
              "delete from tool where barcode = %s"
        params = [barcode, barcode, barcode]

        message = "Tool deleted!"
        return sql, params, message

    elif entity == REQUEST:
        request_id = input("Enter Request ID: ")
        sql = "delete from request_for where request_id=%s;delete from request where request_id=%s"
        params = [request_id, request_id]
        message = "Request deleted!"
        return sql, params, message

    elif entity == CATEGORY:
        name = input("Enter Category Name: ")
        sql = "delete from organizes where name=%s;delete from categories where name=%s"
        params = [name, name]
        message = "Category deleted!"
        return sql, params, message
    else:
        print("Error: Invalid Entity type")
        print("Valid Entity Types: account, tool, request, category")
        return
