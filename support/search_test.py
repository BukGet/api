import httplib
from urllib import urlencode

class Tester(object):
    host = 'bukget.org'
    port = 80
    
    def check(self, fieldname, action, value):
        http = httplib.HTTPConnection(self.host, port=self.port)
        payload = urlencode({
            'fieldname': fieldname,
            'action': action,
            'value': value
        })
        headers = {'Content-Length': len(payload),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        http.request('POST', '/api/search', body=payload, headers=headers)
        resp = http.getresponse()
        print resp.read()

if __name__ == '__main__':
    bukget = Tester()
    bukget.check('authors', 'in', 'LordNed')
    bukget.check('v_game_builds', 'in', '1337')
    bukget.check('name', 'like', 'essential')
    bukget.check('v_md5', '=', '2032eabffbe58378a3393e4ed881e462')
    bukget.check('v_date', '>=', '1314231157')
    