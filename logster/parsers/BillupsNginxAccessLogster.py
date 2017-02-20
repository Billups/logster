###  A logster parser file that can be used to count the number
###  of response codes found in an Nginx access log.
###
###  For example:
###  sudo ./logster --dry-run --output=ganglia BillupsNginxAccessLogster /var/log/nginx/access.log
###

import time
import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class BillupsNginxAccessLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.total_requests = 0
        self.http_1xx = 0
        self.http_2xx = 0
        self.http_3xx = 0
        self.http_4xx = 0
        self.http_5xx = 0
        
        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (in this case, http_status_code).
        self.access_log_entry_reg = re.compile('^\[.*\]\s+(?P<client_ip>[\d\.]+)\s+[\S-]+\s+(?P<http_host>[\w\.]+)[\S]+\s+\"{1}(?P<request_uri>[\S]+)\"{1}\s+(?P<http_status>\d+)\s+(?P<bytes_sent>\d+)\s+(?P<response_time_seconds>[\d\.]+)\s+\"{1}(?P<http_referrer>\S+)\"{1}\s+\"{1}(?P<user_agent>.+)\"{1}$')


    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            print line

            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.access_log_entry_reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()

                self.total_requests += 1

                status = int(linebits['http_status'])

                if (status < 200):
                    self.http_1xx += 1
                elif (status < 300):
                    self.http_2xx += 1
                elif (status < 400):
                    self.http_3xx += 1
                elif (status < 500):
                    self.http_4xx += 1
                else:
                    self.http_5xx += 1

            else:
                raise LogsterParsingException("regmatch failed to match")

        except Exception as e:
            raise LogsterParsingException("regmatch or contents failed with %s" % e)


    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = float(duration)

        # Return a list of metrics objects
        return [
            MetricObject("total_requests", (self.total_requests / self.duration), "Requests per sec"),
            MetricObject("http_1xx", (self.http_1xx / self.duration), "Responses per sec"),
            MetricObject("http_2xx", (self.http_2xx / self.duration), "Responses per sec"),
            MetricObject("http_3xx", (self.http_3xx / self.duration), "Responses per sec"),
            MetricObject("http_4xx", (self.http_4xx / self.duration), "Responses per sec"),
            MetricObject("http_5xx", (self.http_5xx / self.duration), "Responses per sec"),
        ]

