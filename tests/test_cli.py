# Copyright (C) 2012  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#

import base
import dnf.cli.cli
import mock
import optparse
import unittest

OUTPUT="""\
  Installed: pepper-0:20-0.x86_64 at 1970-01-01 00:00
  Built    :  at 1970-01-01 00:00

  Installed: tour-0:5-0.noarch at 1970-01-01 00:00
  Built    :  at 1970-01-01 00:00
"""

class VersionString(unittest.TestCase):
    def test_print_versions(self):
        yumbase = base.MockYumBase()
        with mock.patch('sys.stdout') as stdout,\
                mock.patch('dnf.sack.rpmdb_sack', return_value=yumbase.sack):
            dnf.cli.cli.print_versions(['pepper', 'tour'], yumbase)
        written = ''.join([mc[1][0] for mc in stdout.method_calls
                           if mc[0] == 'write'])
        self.assertEqual(written, OUTPUT)

class Cli(unittest.TestCase):
    def setUp(self):
        self.yumbase = base.MockYumBase("main")
        self.cli = dnf.cli.cli.Cli(self.yumbase)

    def test_knows_upgrade(self):
        upgrade = self.cli.cli_commands['upgrade']
        update = self.cli.cli_commands['update']
        self.assertIs(upgrade, update)

    def test_configure_repos(self):
        opts = optparse.Values()
        opts.nogpgcheck = True
        opts.repos_enabled = []
        opts.repos_disabled = []
        self.cli._configure_repos(opts)
        self.assertTrue(self.yumbase._override_sigchecks)
        self.assertTrue(self.yumbase.repos.getRepo("main")._override_sigchecks)

@mock.patch('dnf.yum.Base.doLoggingSetup', new=mock.MagicMock)
class TestConfigure(unittest.TestCase):
    def setUp(self):
        self.yumbase = base.MockYumBase("main")
        self.cli = dnf.cli.cli.Cli(self.yumbase)

    def test_configure(self):
        """ Test Cli.configure.

            For now just see that the method runs.
        """
        self.cli.configure(['update'])
        self.assertEqual(self.cli.cmdstring, "dnf update ")

    def test_configure_verbose(self):
        self.cli.configure(['-v', 'update'])
        self.assertEqual(self.cli.cmdstring, "dnf -v update ")
        self.assertEqual(self.yumbase.conf.debuglevel, 6)
        self.assertEqual(self.yumbase.conf.errorlevel, 6)
