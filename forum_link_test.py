#!/usr/bin/env python
 
import httplib, urllib

class XenForo(object):
  host      = None
  username  = None
  password  = None
  cookies   = {}
  headers   = {
   'Cache-Control': 'max-age=0',
 'Accept-Language': 'en-US,en;q=0.8',
  'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept': 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
      'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-US) '+\
                    'AppleWebKit/534.16 (KHTML, like Gecko) '+\
                    'Chrome/10.0.648.205 Safari/534.16',
  }
  
  def __init__(self, username, password, host):
    self.username = username
    self.password = password
    self.host     = host
  
  def _update_cookies(self, cookies):
    print cookies
    if cookies is not None:
      for cookie in cookies.split(';'):
        dset        = cookie.split('=')
        if len(dset) > 1:
          if dset[0] in ['f_user', 'f_session', 'IDstack']:
            self.cookies[dset[0]] = dset[1]
  
  def _logged_in(self, page):
    if page[:100].find('class="Public LoggedOut"') > -1:
      return False
    elif page[:100].find('class="Public LoggedIn"') > -1:
      return True
    else:
      return 'UNKNOWN'
  
  def _get_cookies(self):
    cookies = []
    for cookie in self.cookies:
      cookies.append('%s=%s; ' % (cookie, self.cookies[cookie]))
    print '; '.join(cookies)
    return '; '.join(cookies)
  
  def _get(self, loc):
    con           = httplib.HTTPConnection(self.host)
    cookies       = self._get_cookies()
    headers       = self.headers
    if cookies is not '':
      headers['Cookie'] = cookies
    con.request('GET', loc, headers=headers)
    resp          = con.getresponse()
    print resp.getheaders()
    self._update_cookies(resp.getheader('set-cookie'))
    newloc        = resp.getheader('location')
    if newloc is not None:
      print 'Chasing Referral: %s' % newloc
      page        = self._get(newloc)
    else:
      page        = resp.read()
    return page
  
  def _post(self, loc, formdata):
    con           = httplib.HTTPConnection(self.host)
    cookies       = self._get_cookies()
    headers       = self.headers
    payload       = urllib.urlencode(formdata)
    if cookies is not '':
      headers['Cookie']       = cookies
    headers['Host']           = 'forums.bukkit.org'
    headers['Origin']         = 'http://forums.bukkit.org/'
    headers['Referer']        = 'http://forums.bukkit.org/'
    headers['Content-Type']   = 'application/x-www-form-urlencoded'
    headers['Content-Length'] = len(payload)
    print headers
    con.request('POST', loc, headers=headers, body=payload)
    resp          = con.getresponse()
    print resp.getheaders()
    self._update_cookies(resp.getheader('set-cookie'))
    newloc        = resp.getheader('location')
    if newloc is not None:
      print 'Chasing Referral: %s' % newloc
      page        = self.__get(newloc)
    else:
      page        = resp.read()
    return page
  
  def login(self):
    self.__get('/')
    formdata  = {
         'login': self.username,
      'register': 0,
      'password': self.password,
      'remember': 0,
  'cookie_check': 1,
      'redirect': '/',
      '_xfToken': '',
    }
    page = self._post('/login/login', formdata)
    return self._logged_in(page)
  
  def private_message(self, user, message, locked=False):
    pass
    
    

if __name__ == '__main__':
  forum   = XenForo('XXX', 'XXX', 'forums.bukkit.org')
  print forum.login()
  print forum.cookies
