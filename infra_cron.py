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
import os

from jinja2 import Environment

import githubutils as gh

def titlesub(title_str):
    return '=' * len(title_str)

env = Environment()
env.filters['titlesub'] = titlesub


# Get your own token here:  https://github.com/settings/applications
token = os.environ.get('GH_OAUTH_TOKEN')
template = 'template.html'
repos = gh.get_repos('fedora-infra', token)


output = {}
for repo in repos:
    pulls = gh.get_pulls('fedora-infra', repo['name'], token)
    output[repo['name']] = pulls


# Read in template
stream = open(template, 'r')
tplfile = stream.read()
stream.close()


# Fill the template
mytemplate = env.from_string(tplfile)
html = mytemplate.render(
    projects=output,
    date=datetime.datetime.now().strftime("%a %b %d %Y %H:%M")
)


# Write down the page
stream = open('index.html', 'w')
stream.write(html)
stream.close()

