
def top_lent(curs):
    curs.execute("select t.name, sum(duration) as total_duration, avg(duration) as average_duration from " \
                 "request_for rf left join request r on (r.request_id = rf.request_id) left join tool t on t.barcode = rf.barcode " \
                 "group by t.name order by total_duration desc")
    result = curs.fetchall()
    print("Top 10 Time Lent:")
    for i in range(10):
        percent = (result[i][1] / (5 * 365)) * 100
        print("\t", i + 1, " ", result[i][0], "was lent %f%s of the time, a total %d of days, for an average of %d days per request" %(percent, '%', result[i][1], result[i][2]))

def top_borrowed(curs):

    curs.execute("select t.name, t.barcode, count(r.barcode) from tool as t left outer join request_for as r on " \
                 "(t.barcode = r.barcode) group by t.barcode order by count(r.barcode) desc")
    result = curs.fetchall()
    print("Top 10 Most Frequently Borrowed:")
    for i in range(10):
        print("\t", i + 1, " ", result[i][0], "was borrowed %d times" %(result[i][2]))
