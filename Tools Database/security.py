
def jenkins_hash(string):
    hash = 0
    length = len(string)
    i = 0

    while i < length:
        hash += ord(string[i])
        hash &= 0xFFFFFFFF
        hash += hash << 11
        hash &= 0xFFFFFFFF
        hash ^= hash >> 6
        hash &= 0xFFFFFFFF
        i += 1

    hash += hash << 3
    hash &= 0xFFFFFFFF
    hash ^= hash >> 11
    hash &= 0xFFFFFFFF
    hash += hash << 15
    hash &= 0xFFFFFFFF

    return hash


def get_hash(username, password):
    hash_str = username + password

    hash_val = jenkins_hash(hash_str)

    return hash_val

def hash_data(conn, curs):
    curs.execute("select username, password from account")
    users = curs.fetchall()

    for u in users:
        username = u[0]
        password = u[1]

        hash_pw = get_hash(username, password)
        params = [str(hash_pw), username]
        print(params)
        curs.execute('UPDATE account SET password = %s WHERE username=%s', params)
        conn.commit()

