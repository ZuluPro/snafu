from datetime import datetime

def logprint(string='', color='default') :
    colors = {
        'default' : "0",
        'red' : "0;31",
        'green' : "0;32",
        'yellow' : "0;33",
        'pink' : "0;35"
    }
  
    print '\033['+colors[color]+'m'+ datetime.strftime(datetime.now(), '[%d/%b/%Y %X] ')+string+ '\033[0m'
