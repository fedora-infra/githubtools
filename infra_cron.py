#!/usr/bin/env python -tt
#-*- coding: utf-8 -*-
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
This program retrieves all the open pull-request for all the project present
under the fedora-infra organisation on github, the list of pull-requests are
then presented in a HTML page using the template ``template.html`` present in
this folder.

run it as:

::

    GH_OAUTH_TOKEN="<your github token>" python infra_cron.py
"""

import datetime
import logging
import os
import sys

import arrow
from dateutil import tz
from dateutil.parser import parse
from jinja2 import Environment

import githubutils as gh

env = Environment()
logging.basicConfig()
LOG = logging.getLogger("pkgdb")
LOG.setLevel(logging.INFO)
if '--debug' in sys.argv:
    log.setLevel(logging.DEBUG)

if '-h' in sys.argv or '--help' in sys.argv:
    print 'Run the command alone or with --debug for more information about '\
        'what\'s going on'
    sys.exit()


def titlesub(title_str):
    """ Returns the underline line for a title. """
    return '=' * len(title_str)


env.filters['titlesub'] = titlesub


def ago(date):
    """ Returns how long ago was this date. """
    delta = datetime.datetime.now(tz.tzutc()) - date
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '%s:%s:%s ago' % (hours, minutes, seconds)


env.filters['ago'] = ago

# Get your own token here:  https://github.com/settings/applications
token = os.environ.get('GH_OAUTH_TOKEN')
template = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'template.html')
LOG.info('Retrieve fedora-infra repo list')
repos = gh.get_repos('fedora-infra', token)


output = {}
total = 0
for repo in repos:
    LOG.info('Query repo: %s', repo['name'])
    pulls = []
    for pull in gh.get_pulls('fedora-infra', repo['name'], token):
        LOG.info('Query repo pr: %s/%s', repo['name'], pull['number'])
        pull['comments'] = gh.get_comments('fedora-infra', repo['name'],
                                            pull['number'], token)
        pull['created_at'] = arrow.get(pull['created_at'])
        if 'updated_at' in pull:
            pull['updated_at'] = arrow.get(pull['updated_at'])
        pulls.append(pull)
    if pulls:
        output[repo['name']] = pulls
        total += len(pulls)


# Read in template
stream = open(template, 'r')
tplfile = stream.read()
stream.close()


# Fill the template
mytemplate = env.from_string(tplfile)
html = mytemplate.render(
    projects=output,
    total=total,
    date=datetime.datetime.utcnow().strftime("%a %b %d %Y %H:%M")
)


# Write down the page
stream = open(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'index.html'), 'w')
stream.write(html)
stream.close()

