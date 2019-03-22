import os

import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize("name,version", [
    ("epel-release", "7"),
    ("fail2ban", "0.9.6"),
    ("fail2ban-firewalld", "0.9.6"),
    ("fail2ban-hostsdeny", "0.9.6"),
    ("fail2ban-mail", "0.9.6"),
    ("fail2ban-server", "0.9.6"),
    ("fail2ban-sendmail", "0.9.6"),
    ("fail2ban-systemd", "0.9.6")
])
def test_fail2ban_packages(host, name, version):
    pkg = host.package(name)
    assert pkg.is_installed
    assert pkg.version.startswith(version)


def test_fail2ban_local_configuration_file(host):
    f = host.file('/etc/fail2ban/fail2ban.local')

    assert f.exists
    assert f.is_file
    assert f.mode == 0o644
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.contains('loglevel     = WARNING')
    assert f.contains('logtarget    = /var/log/fail2ban.log')
    assert f.contains('dbpurgeage   = 648000')


def test_fail2ban_local_jail_configuration_file(host):
    f = host.file('/etc/fail2ban/jail.d/00-default.local')

    assert f.exists
    assert f.is_file
    assert f.mode == 0o644
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.contains('ignoreip       = 127.0.0.0/8 192.168.0.0/24')
    assert f.contains('bantime        = 14400')
    assert f.contains('findtime       = 300')
    assert f.contains('maxretry       = 5')
    assert f.contains('destemail      = fail2ban@molecule.test')
    assert f.contains('mta            = sendmail')
    assert f.contains('protocol       = tcp')
    assert f.contains('chain          = INPUT')
    # TODO: implement tests for default and custom actions
    assert f.contains('action         = %(action_)s')


def test_fail2ban_custom_actions_file(host):
    f = host.file('/etc/fail2ban/action.d/99-molecule.local')

    assert f.exists
    assert f.is_file
    assert f.mode == 0o644
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.contains('actionstart    = /bin/start')
    assert f.contains('actionstop     = /bin/stop')
    assert f.contains('actioncheck    = /bin/check')
    assert f.contains('actionban      = /bin/ban')
    assert f.contains('actionunban    = /bin/unban')


def test_fail2ban_custom_filters_file(host):
    f = host.file('/etc/fail2ban/filter.d/99-molecule.local')

    assert f.exists
    assert f.is_file
    assert f.mode == 0o644
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.contains('before         = /foo/before')
    assert f.contains('after          = /foo/after')
    assert f.contains('failregex      = azerty.*')
    assert f.contains('ignoreregex    = qwerty.*')
