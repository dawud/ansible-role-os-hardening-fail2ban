# Fail2ban IPS installation and configuration

Adds an Fail2ban IPS service to your project.

[`fail2ban`](http://www.fail2ban.org/) is a service which parses specified log
files and can perform configured actions when a given [regexp](https://en.wikipedia.org/wiki/Regular_expression) is found.
It's usually used to ban offending IP addresses using `iptables` rules
(only IPv4 connections are supported at the moment).

[Note that](https://access.redhat.com/solutions/267483), at the time of this
writing, Fail2ban is not supported or offered in Red Hat repositories.
However, many IPS solutions, including Fail2ban, are available
from other vendors or via Extra Packages for Enterprise Linux (EPEL).

## Requirements

None. The required packages are managed by the role.

## Role Variables

- From `defaults/main.yml`

```yaml
---
## Fail2ban IDS
# Set the package install state for distribution packages
# Options are 'present' and 'latest'
security_package_state: present
# start on boot
security_rhel7_fail2ban_service_enabled: 'yes'
# current state: started, stopped
security_rhel7_fail2ban_service_state: started

## src:  `/etc/fail2ban/fail2ban.local.j2`
## dest: `/etc/fail2ban/fail2ban.local`
# Log verbosity
# valid values : CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG. Default: ERROR
security_rhel7_fail2ban_loglevel: 'WARNING'
# Where to save logs: a file, ``STDOUT``, ``STDERR``, ``SYSLOG``
security_rhel7_fail2ban_logtarget: '/var/log/fail2ban.log'
# The following value increases the default dbpurgeage defined in fail2ban.conf
# to e.g. 648000 (7.5 days) to maintain entries for failed logins for sufficient
# amount of time so that the 'recidive' jail for more extended banning of
# persistent abusers can be used.
# Make sure that your loglevel specified in fail2ban.local (above)
# is not at DEBUG level -- which might then cause fail2ban to fall into
# an infinite loop constantly feeding itself with non-informative lines
security_rhel7_fail2ban_dbpurgeage: '648000'

## src:  `/etc/fail2ban/jail.d/default.local.j2`
## dest: `/etc/fail2ban/jail.d/00-default.local`
# List of default IP addresses or CIDR networks which should be ignored by
# fail2ban
security_rhel7_fail2ban_ignoreip_default: ['127.0.0.0/8']
# List of IP addresses or CIDR networks which should be ignored by fail2ban
security_rhel7_fail2ban_ignoreip: []
# Length of time in seconds for the ban to persist (by default, 2 hours)
security_rhel7_fail2ban_bantime: '{{ (60 * 60 * 2) }}'
# Length of time in seconds between bad login attempts to consider for banning
# (by default, 10 minutes)
security_rhel7_fail2ban_findtime: '{{ (60 * 10) }}'
# Maximum number of bad login attempts in the given ``findtime`` to trigger
# a ban
security_rhel7_fail2ban_maxretry: '3'
# Recipient address of e-mail notifications
security_rhel7_fail2ban_destemail: 'fail2ban@{{ ansible_domain }}'
# Default mail notification method
security_rhel7_fail2ban_mta: 'sendmail'
# fail2ban_banaction: iptables-multiport
# Protocol type to filter in ``iptables``: ``tcp``, ``udp``, ``icmp``, ``all``
security_rhel7_fail2ban_protocol: 'tcp'
# `iptables` chain to add the rules in
security_rhel7_fail2ban_chain: 'INPUT'
# Action performed by ``fail2ban`` when IP address is banned. See list of
# default actions below.
security_rhel7_fail2ban_action: 'action_'
# Dict with set of named actions to perform when a ban is executed.
# Example:
# yamllint disable rule:line-length
# security_rhel7_fail2ban_default_actions:
#   # Block an IP address in the firewall
#   'action_': |
#     %(banaction)s[name=%(__name__)s, port="%(port)s", protocol="%(protocol)s", chain="%(chain)s", position="%(position)s", bantime="%(bantime)s"]
#   # Block an IP address in the firewall and send a notification about the
#   # offender taken from ``whois``
#   'action_mw': |
#     %(banaction)s[name=%(__name__)s, port="%(port)s", protocol="%(protocol)s", chain="%(chain)s", position="%(position)s", bantime="%(bantime)s"]
#     %(mta)s-whois[name=%(__name__)s, dest="%(destemail)s", protocol="%(protocol)s", chain="%(chain)s"]
#   # Block an IP address in the firewall and send a notification about the
#   # offender taken from ``whois`` and relevant log entries
#   # yamllint disable-line rule:line-length
#   'action_mwl': |
#     %(banaction)s[name=%(__name__)s, port="%(port)s", protocol="%(protocol)s", chain="%(chain)s", position="%(position)s", bantime="%(bantime)s"]
#     %(mta)s-whois-lines[name=%(__name__)s, dest="%(destemail)s", logpath=%(logpath)s, chain="%(chain)s"]
# yamllint enable rule:line-length
security_rhel7_fail2ban_default_actions: {}
# Dict with custom set of named actions to perform when a ban is executed.
security_rhel7_fail2ban_custom_actions: {}

## src:  `/etc/fail2ban/action.d/action.local.j2`
## dest: `/etc/fail2ban/action.d/{{ item.filename }}.local`
# List of dicts which define custom local ``fail2ban`` actions.
security_rhel7_fail2ban_actions: []

## src:  `/etc/fail2ban/filter.d/filter.local.j2`
## dest: `/etc/fail2ban/filter.d/{{ item.filename }}.local`
# List of dicts which define custom local ``fail2ban`` filters.
security_rhel7_fail2ban_filters: []

## src:  `/etc/fail2ban/jail.d/jail.local.j2`
## dest: `/etc/fail2ban/jail.d/{{ item.filename }}.local`
# List of dicts which define ``fail2ban`` jails.
security_rhel7_fail2ban_jails:
  - name: 'sshd'
    enabled: 'true'
  - name: 'selinux-ssh'
    enabled: 'true'
  - name: 'recidive'
    enabled: 'true'
  - name: 'pam-generic'
    enabled: 'true'
```

- From `vars/main.yml`

```yaml
---
# RHEL 7 STIG: Packages to add/remove
stig_packages_rhel7:
  - packages:
      - fail2ban
      - fail2ban-firewalld
      - fail2ban-hostsdeny
      - fail2ban-mail
      - fail2ban-sendmail
      - fail2ban-server
      - fail2ban-systemd
      - whois
    state: "{{ security_package_state }}"
    enabled: 'True'

# Local actions
fail2ban_actions: "{{ security_rhel7_fail2ban_actions }}"
# Local filters
fail2ban_filters: "{{ security_rhel7_fail2ban_filters }}"
# Local jails
fail2ban_jails: "{{ security_rhel7_fail2ban_jails }}"
```

## fail2ban_actions

List of local `fail2ban` actions that should be present or absent when configuring
`fail2ban`. Each action is defined as a YAML dict with the following keys:

`name`
  Required. Name of the action.

`ban`
  Required. Command executed when banning an IP. Take care that the command is executed
  with `fail2ban` user rights.

`check`
  Optional. Command executed once before each `ban` command.

`filename`
  Optional. Alternative name of the action configuration file.

`start`
  Optional. Command executed once at the start of `fail2ban`.

`state`
  Optional. If `present`, the action will be created when configuring `fail2ban`.
  If `absent`, the action will be removed when configuring `fail2ban`.

`stop`
  Optional. Command executed once at the end of `fail2ban`.

`unban`
  Optional. Command executed when unbanning an IP. Take care that the command is executed
  with `fail2ban` user rights.


## fail2ban_filters

List of local `fail2ban` filters that should be present or absent when configuring
`fail2ban`. Each filter is defined as a YAML dict with the following keys:

`name`
  Required. Name of the filter.

`after`
  Optional. Specify an addtional filter configuration file that `fail2ban` will
  read after reading this filter configuration filer.

`before`
  Optional. Specify an addtional filter configuration file that `fail2ban` will
  read before reading this filter configuration file.

`definitions`
  Optional. Custom definitions used by the filter.

`failregex`
  Required. Regular expression(s) used by the filter to detect break-in attempts.
  You can have the filter try to match multiple regular expressions. Each regular
  expression should be on its own line.

`filename`
  Optional. Alternative name of the filter configuration file. If not specfied, it
  will use the `name` of the filter.

`ignoreregex`
  Optional. Regular expression(s) used to filter out invalid break-in attempts. You
  can have the filter try to match multiple regular expressions. Each regular
  expression should be on its own line.

`state`
  Optional. If `present`, the filter will be created when configuring `fail2ban`.
  If `absent`, the filter will be removed when configuring `fail2ban`.


## fail2ban_jails

Jails are defined in the form of dicts, where dict keys are the option names
and dict values are option values. You can specify values either as strings or
YAML lists, in which case elements of the list will be separated by commas.

Some keys have a special meaning:

`name`
  Jail name, used as a section header and part of the filename. Required.

`filename`
  Alternative file name, optional.

`comment`
  A commented text added before the given jail

`delete`
  If this option is present and `True`, file which defines a given jail will
  be deleted

`ignoreip`
  **List** of IP addresses or CIDR subnets which should be ignored by
  `fail2ban`

`action`
  It should be a name of a default or custom action, which will be used by
  `fail2ban`

Other options are the same as normal `fail2ban` jail configuration options.
Refer to default `/etc/fail2ban/jail.conf` or [`fail2ban wiki`](http://www.fail2ban.org/wiki/index.php/MANUAL_0_8#Jails) for possible
options.


## Examples:

Enable `ssh` jail and configure it to send mail messages about banned hosts::

```yaml
    fail2ban_jails:

      - name: 'ssh'
        enabled: 'true'
        action: 'action_mw'
```

Enable `dovecot` jail with custom filename and send mail notifications to
postmaster::


```yaml
    fail2ban_jails:

      - name: 'dovecot'
        filename: '50_dovecot'
        enabled: 'true'
        destemail: 'postmaster@{{ ansible_domain }}'
```


## Dependencies

This role depends on `ansible-os-epel`.

## Example Playbook

Example of how to use this role:

```yml
    - hosts: servers
      roles:
         - { role: ansible-os-hardening-fail2ban }
```

## Contributing

This repository uses [git-flow](http://nvie.com/posts/a-successful-git-branching-model/).
To contribute to the role, create a new feature branch (`feature/foo_bar_baz`),
write [Molecule](http://molecule.readthedocs.io/en/master/index.html) tests for the new functionality
and submit a pull request targeting the `develop` branch.

Happy hacking!

## License

GPLv3, as part of this work is derived from [debops/ansible-fail2ban](https://github.com/debops/ansible-fail2ban)

## Author Information

[David Sastre](david.sastre@redhat.com)
