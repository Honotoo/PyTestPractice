import json
import time


def get_time():
    ttt=(str("{}-{}-{}_{}-{}".format(time.localtime().tm_year, time.localtime().tm_mon,
                                             time.localtime().tm_mday, time.localtime().tm_hour,
                                             time.localtime().tm_min, )))
    return ttt


def SerializeMeThis(data, insertTime = False):
    if insertTime == True:
        Card = data["payment"]["paymentData"].split("/")[0]
        Time = data["payment"]["paymentData"].split("/")[1]
        paymentData = Card + "/" + get_time()
        data["payment"]["paymentData"] = paymentData
        return json.dumps(data)
    else :
        return json.dumps(data)









# def SerializeMeThis():
#     with open("datafile.json", "w") as write:
#         json.dump(data, write)

