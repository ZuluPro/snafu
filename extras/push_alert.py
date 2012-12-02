#!/usr/bin/env python
#    By Anthony MONTHE montheanthony@hotmail.com 
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER "AS IS" AND
#    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER BE LIABLE FOR
#    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from xmlrpclib import ServerProxy
from sys import argv,exit
from os import uname
from re import match

def get_help():
    return """
    Example :
        push_alert -H 'http://snafu/snafu/webservice' -h myHost -s myService -S WARNING -d '10-13-2000 00:30:28)' -i 'MYINFO'

    Option :
    -w | --webservice : Snafu webservice's URL
    -h | --host : Nagios host's name ($HOSTNAME$)
    -s | --service : Nagios service's name ($SERVICEDISPLAYNAME$)
    -S | --status : Nagios service's status ($SERVICESTATE$)
    -d | --date : Alert's date ($SHORTDATETIME$)
    -i | --info : Alert's information ($SERVICEOUTPUT$)
    --help : This help message
    """

if __name__ == '__main__':
    try:
        del argv[0]
        while argv :
            arg = argv.pop(0)
            if match(r'^(-w|--webservice)$', arg) :
                snafu_url = argv.pop(0)
            elif match('^(-h|--host)$', arg) :
                host = argv.pop(0)
            elif match(r'^(-s|--service)$', arg) :
                service = argv.pop(0)
            elif match(r'^(-S|--status)$', arg) :
                status = argv.pop(0)
            elif match(r'^(-d|--date)$', arg) :
                date = argv.pop(0)
            elif match(r'^(-i|--info)$', arg) :
                info = argv.pop(0)
            elif arg == '--help' :
                print get_help()
                exit(0)
            else :
                print 'Invalid argument !'
                print get_help()
                exit(1)

    except IndexError:
        print "Error in arguments !"
        print get_help()
        exit(1)
        
    server = ServerProxy(snafu_url)
    supervisor = uname()[1] 
    try:
        server.pushAlert(
          host,
          service,
          status,
          info,
          supervisor,
          date
        )
        exit(0)
    except NameError:
        print "Missing arguments !"
        print get_help()
