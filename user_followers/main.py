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

    account_username = bot.account_username
    for i in range(0, 100):

        unlike_done = bot.unlike_media(account_username)
        bot.write_log(str(i) + " - UNLIKE DONE: " + str(unlike_done))
        bot.bot_sleep(i)

    quit()

