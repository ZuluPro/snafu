#!/bin/bash
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

function get_help {
  echo "
    Example :
        push_alert.sh -w 'snafu.com' -h myHost -s myService -S WARNING -d '02-06-2012 16:30:28)' -i 'MYINFO'

    Option :
    -w | --webservice : Snafu webservice's URL
    -p | --port : Snafu webservice's port (default=80)
    -h | --host : Nagios host's name (\$HOSTNAME\$)
    -s | --service : Nagios service's name (\$SERVICEDISPLAYNAME\$)
    -S | --status : Nagios service's status (\$SERVICESTATE\$)
    -d | --date : Alert's date (\$SHORTDATETIME\$)
    -i | --info : Alert's information (\$SERVICEOUTPUT\$)
    --help : This help message
";
}

# Walk on all arguments
while (( "$#" )) ; do
  case $1 in
    -w|--webservice) snafu=$2 ;;
    -p|--port) port=$2 ;;
    -h|--host) host=$2 ;;
    -s|--service) service=$2 ;;
    -S|--status) status=$2 ;;
    -d|--date) date=$2 ;;
    -i|--info) info=$2 ;;
    --help)
      get_help
      exit 0
    ;;
    *)
      echo 'Invalid in arguments !'
      get_help
      exit 1
    ;;
  esac
  shift 2
done

# Check if there's no missing args
[[ -z "$port" ]] && port=80
[[ -z "$date" ]] && date=$(date "+%Y-%m-%d %H:%M:%S")
if [[ -z "$snafu" || -z "$host" || -z "$service" || -z "$status" || -z "$date" || -z "$info" ]] ; then
  echo 'Missing arguments !'
  get_help
  exit 1
fi

# Make an XML-RPC message
msg="\n<?xml version='1.0'?>\n<methodCall>\n<methodName>pushAlert</methodName>\n<params>\n<param>\n<value><string>$host</string></value>\n</param>\n<param>\n<value><string>$service</string></value>\n</param>\n<param>\n<value><string>$status</string></value>\n</param>\n<param>\n<value><string>$info</string></value>\n</param>\n<param>\n<value><string>$(uname -n)</string></value>\n</param>\n<param>\n<value><string>$date</string></value>\n</param>\n</params>\n</methodCall>"

# Count message's length for put it in header
length=$(echo -e $msg|wc -c)
# Make header, with 'bash script' as HTTP client
header="POST /snafu/webservice HTTP/1.1\nHost: $snafu\nUser-Agent: bash script\nContent-Type: text/xml\nContent-length: $length\n"

# Test ro contact SNAFU server
nc -z $snafu $port

# If contact is OK, send header with message.
if [[ $? == 0 ]] ; then
  echo -e ${header}${msg} | nc -w 1 $snafu $port > :
  exit 0
else
  echo "Snafu unreachable !"
  exit 1
fi
