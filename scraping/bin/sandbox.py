import time
import calendar
for i in range(10):
    print('\r{}'.format(calendar.timegm(time.gmtime())))
    time.sleep(1)