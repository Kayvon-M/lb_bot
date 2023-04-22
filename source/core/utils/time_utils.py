import datetime


def getNowAsStr():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def dateStrToDateTime(dateStr):
    return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
