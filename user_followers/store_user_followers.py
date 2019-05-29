#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Use text editor to edit the script and type in valid Instagram username/password
import sys
sys.path.insert(0, '../InstagramAPI')


import ConfigParser
from like_follower_bot import LikeFollowersBot

if __name__ == '__main__':

    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('./config.properties')
    bot = LikeFollowersBot(config)
    api = bot.login_to_instagram()

    if not bot.api.isLoggedIn:
        bot.write_log("LOGIN ERROR" + str(bot.account_username) + "/" +  str(bot.account_password))
        quit()

    # ricerca dal proprio account
    username_to_search = bot.account_username

    # ricerca da account concorrenza
    #username_to_search = "almadanza_bologna"x
    #username_to_search = "lisa.mazzoni"
    stored = bot.store_all_follower_info(username_to_search)
    bot.write_log("STORED FOLLOWER : " + str(stored))