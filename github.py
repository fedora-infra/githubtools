#!/usr/bin/env python

import os

# Get your own token here:  https://github.com/settings/applications
token = os.environ.get('GH_OAUTH_TOKEN',
                       "<your own github token>")

import githubutils as gh
repos = gh.get_repos('fedora-infra', token)

for repo in repos:
    pulls = gh.get_pulls('fedora-infra', repo['name'], token)
    for pull in pulls:
        print
        print "-", repo['name'], "#%i" % pull['number']
        print " ", pull['title'][:78]
        print " ", pull['issue_url']
