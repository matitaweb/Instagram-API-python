#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Use text editor to edit the script and type in valid Instagram username/password
import sys
sys.path.insert(0, '../InstagramAPI')

import ConfigParser
from like_follower_bot import LikeFollowersBot




if __name__ == '__main__':

    # load configuration
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('./config.properties')
    bot = LikeFollowersBot(config)
    api = bot.login_to_instagram()

    if not api.isLoggedIn:
        bot.write_log("LOGIN ERROR" + str(bot.account_username) + "/" +  str(bot.account_password))
        quit()

    username_to_search = "almadanza_bologna"
    like_done = bot.like_follower_media_user_recursive(username_to_search, 1)
    bot.write_log("LIKE DONE: " + str(like_done))



    quit()

