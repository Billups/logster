from logster.parsers.BillupsNginxAccessLogster import BillupsNginxAccessLogster
from logster.logster_helper import LogsterParsingException
import unittest

class TestBillupsNginxAccessLogster(unittest.TestCase):

    def setUp(self):
        self.logster = BillupsNginxAccessLogster()

    def test_valid_lines(self):
        access_log_tmpl = '[17/Feb/2017:22:08:50 +0000] %s - %s:80 "%s" %s %s %s "-" "%s"'
        self.logster.parse_line(access_log_tmpl % ('192.168.1.101', 'foo.testy.com', '/api/foo?bar=45&baz=-32.0021', '200', '100', '0.001', 'python-requests/2.13.0'))
        self.logster.parse_line(access_log_tmpl % ('192.168.2.101', 'bar.testy.com', '/index.html', '201', '200', '0.002', 'RoflCopterz 2.x'))
        self.logster.parse_line(access_log_tmpl % ('192.168.3.101', 'baz.testy.com', '/api/foo?bar=45&baz=roflcopterz', '302', '300', '0.003', 'InternetExploder 6.x'))

        self.assertEqual(3, self.logster.total_requests)
        self.assertEqual(0.006, self.logster.total_response_time)
        self.assertEqual(0, self.logster.http_1xx)
        self.assertEqual(2, self.logster.http_2xx)
        self.assertEqual(1, self.logster.http_3xx)
        self.assertEqual(0, self.logster.http_4xx)
        self.assertEqual(0, self.logster.http_5xx)

    def test_metrics_1sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(1)
        self.assertEqual(7, len(metrics))

        expected = {
            "total_requests": 3,
            "response_time_avg": 0.002,
            "http_1xx": 0,
            "http_2xx": 2,
            "http_3xx": 1,
            "http_4xx": 0,
            "http_5xx": 0
        }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_metrics_3sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(3)
        self.assertEqual(7, len(metrics))

        expected = {
            "total_requests": 1,
            "response_time_avg": 0.002/3.0,
            "http_1xx": 0,
            "http_2xx": 2.0/3.0,
            "http_3xx": 1.0/3.0,
            "http_4xx": 0,
            "http_5xx": 0
        }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_invalid_line(self):
        self.assertRaises(LogsterParsingException, self.logster.parse_line, 'invalid log entry')

if __name__ == '__main__':
    unittest.main()

