from logster.parsers.BillupsNginxAccessLogster import BillupsNginxAccessLogster
from logster.logster_helper import LogsterParsingException
import unittest

class TestBillupsNginxAccessLogster(unittest.TestCase):

    def setUp(self):
        self.logster = BillupsNginxAccessLogster()

    def test_valid_lines(self):
        #access_log_tmpl = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" %s 2326'
        access_log_tmpl = '[17/Feb/2017:22:08:50 +0000] 172.31.20.116 - zisa.edge.boohma.com:80 "/api/harebrane/v3/products/byboundingbox/find?tl_lat=45.06538059009731&tl_lon=-106.70050400310494&br_lat=38.72751746254360&br_lon=-94.43611157000718" %s 10349 0.225 "-" "python-requests/2.13.0"'
        self.logster.parse_line(access_log_tmpl % '200')
        self.logster.parse_line(access_log_tmpl % '201')
        self.logster.parse_line(access_log_tmpl % '400')
        self.assertEqual(0, self.logster.http_1xx)
        self.assertEqual(2, self.logster.http_2xx)
        self.assertEqual(0, self.logster.http_3xx)
        self.assertEqual(1, self.logster.http_4xx)
        self.assertEqual(0, self.logster.http_5xx)

    def test_metrics_1sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(1)
        self.assertEqual(5, len(metrics))

        expected = {"http_1xx": 0,
                    "http_2xx": 2,
                    "http_3xx": 0,
                    "http_4xx": 1,
                    "http_5xx": 0
                   }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_metrics_2sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(2)
        self.assertEqual(5, len(metrics))

        expected = {"http_1xx": 0,
                    "http_2xx": 1,
                    "http_3xx": 0,
                    "http_4xx": 0.5,
                    "http_5xx": 0
                   }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_invalid_line(self):
        self.assertRaises(LogsterParsingException, self.logster.parse_line, 'invalid log entry')

if __name__ == '__main__':
    unittest.main()

