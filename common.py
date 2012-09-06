from datetime import datetime

def logprint(string='') :
    return datetime.strftime(datetime.now(), '[%d/%b/%Y %X] ')+string
