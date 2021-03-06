#
# Copyright (C) 2010-2017 Samuel Abels
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
A driver for Arista EOS.
"""
import re
from Exscript.protocols.drivers.driver import Driver

# Match following prompt pattern variations:
# NOTE:  Upon first login, EOS does not return \r\n before prompt
# hostname(s1)>
# hostname(s1)#
# hostname(s1)(config)#
# hostname(s1)(vrf:blah)
# hostname(s1)(vrf:blah)(config)#
# hostname>
# hostname#
# hostname(config)#
# hostname(vrf:blah)#
# hostname(vrf:blah)(config)#
#
# Error patterns
# % Invalid input
# % Incomplete command
# % Ambiguous command

_user_re = [re.compile(r'user ?name: ?$', re.I),
            re.compile(r' login: ?$', re.I)]
_password_re = [re.compile(r'[\r\n]Password: ?$', re.I)]
_prompt_re = [re.compile(r'[\r\n]?[\-\w+\.:/]+(?:\([^\)]+\)){,3}[>#] ?$')]
_error_re = [re.compile(r'% ?Error'),
             re.compile(r'% ?Invalid input', re.I),
             re.compile(r'% ?(?:Incomplete|Ambiguous) command', re.I),
             re.compile(r'connection timed out', re.I)]
_login_fail = [r'[Bb]ad secrets?',
               r'denied',
               r'invalid',
               r'too short',
               r'incorrect',
               r'connection timed out',
               r'failed',
               r'failure']
_login_fail_re = [re.compile(r'[\r\n]'
                             + r'[^\r\n]*'
                             + r'(?:' + '|'.join(_login_fail) + r')', re.I)]


class EOSDriver(Driver):

    def __init__(self):
        Driver.__init__(self, 'eos')
        self.user_re = _user_re
        self.password_re = _password_re
        self.prompt_re = _prompt_re
        self.error_re = _error_re
        self.login_error_re = _login_fail_re

    def init_terminal(self, conn):
        conn.execute('terminal dont-ask')
        conn.execute('terminal length 0')

    def auto_authorize(self, conn, account, flush, bailout):
        conn.send('enable\r')
        conn.app_authorize(account, flush, bailout)
