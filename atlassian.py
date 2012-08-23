#!/usr/bin/env python26

import urllib
import urllib2
import json
import subprocess
import base64
import re

"""
This uses the JIRA rest api to close you some sweet jira tickets.
It reads your git commits looking for some common phrasing. 

eg: 
    This super sweet commit was sassy and closes #RAD-1

It will take your commit message, add it to the ticket and then close the ticket.

It uses basic auth { :( } but, you can simply put your information in your config file
and parse it. It should be as follows:

[jira]
    username = sexlexia
    password = kifgetmypants1
    url      = blahasde.com

From there you can rock and roll, never having to see Jira again!
"""


config = subprocess.Popen(['git', 'config', '--list'], stdout=subprocess.PIPE).communicate()[0]
jira_creds = re.compile("jira.*=*")
credentials = re.findall(jira_creds, config)

if len(credentials) < 3:
    print "You don't have your jira credentials set in your config"
    exit(0)

username, password, url = [x.split("=")[-1] for x in credentials]

line = subprocess.Popen(['git', 'log', '-1', 'HEAD', '--pretty=%B'], stdout=subprocess.PIPE).communicate()[0].rstrip("\n")
ticket_regex = re.compile("[closes|fixes|finishes|completes]+ #[[A-Z]+-[0-9]+]*")
ticket = re.findall(ticket_regex, line)

if ticket:
    ticket = ticket[0].split("#")[-1]
    print ticket

    headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (username, password)).replace("\n",""), "Content-Type" : "application/json"}
    try:
        #Add the comment
        data = { "body" : line}
        request = urllib2.Request("https://%s/rest/api/latest/issue/%s/comment" % (url, ticket), json.dumps(data), headers)
        result = urllib2.urlopen(request)
        result.close()

        data = {"transition": { "id" : 5 } }
        request = urllib2.Request("https://%s/rest/api/latest/issue/%s/transitions" % (url, ticket), json.dumps(data), headers)
        result = urllib2.urlopen(request)
        result.close()

    except urllib2.HTTPError as e:
        print "Bad request :("
        print e.read()
        e.close()
