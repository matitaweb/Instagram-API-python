#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Use text editor to edit the script and type in valid Instagram username/password
import sys
sys.path.insert(0, '../InstagramAPI')

import ConfigParser
from like_follower_bot import LikeFollowersBot


class ReportItem(object):
    username = ""
    photo_of_you = False
    like_count = 0

    # The class "constructor" - It's actually an initializer
    def __init__(self, user, item):
        self.username = str(user['username'])
        self.photo_of_you = item['photo_of_you']
        self.like_count = item['like_count']
        self.user = user
        self.item = item

    def __repr__(self):
        return "<ReportItem username:%s like_count:%s>" % (self.username, self.like_count)

    def __str__(self):
        return "ReportItem: username is %s, like_count is %s" % (self.username, self.like_count)

if __name__ == '__main__':

    # load configuration
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('./config.properties')
    bot = LikeFollowersBot(config)
    api = bot.login_to_instagram()

    if not api.isLoggedIn:
        bot.write_log("LOGIN ERROR" + str(bot.account_username) + "/" +  str(bot.account_password))
        quit()

    res = api.getHashtagFeed("ladanzainvacanza2018")
    bot.write_log("LIKE DONE: " + str(res))
    bot.write_log(api.LastJson)
    items = api.LastJson['items']

    reportItemList = []
    for item in items:
        user = item['user']
        reportItem = ReportItem(user, item)
        #bot.write_log(str(user['username']) + ": (" + str(item['photo_of_you']) +  ") -> " +str(item['like_count']))
        reportItemList.append(reportItem)

    reportItemList.sort(key=lambda x: x.like_count, reverse=True)
    bot.write_log(reportItemList)
    quit()

