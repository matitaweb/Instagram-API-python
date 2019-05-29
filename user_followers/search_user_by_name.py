#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Use text editor to edit the script and type in valid Instagram username/password
import sys
import csv
import random
from datetime import datetime, timedelta

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

from math import cos, asin, sqrt

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))

def checkInteresting(bot, username_id, max_media_loaded_by_user, minTimestamp, contains, lat1, lng1, max_dist):

    all_media_by_user = bot.get_total_user_feed(username_id, max_media_loaded_by_user, minTimestamp)
    for e in all_media_by_user:
        if 'caption' in e and e['caption'] is not None and 'text' in e['caption'] and e['caption']['text'] is not None:
            caption_text = e['caption']['text']
            for c in contains:
                if c.lower() in caption_text.lower() :
                    return True

        if 'lat' in e and  e['lat'] is not None:
            lat2 = e['lat'] #44.5059073
            lng2 = e['lng'] #11.3411807
            d = distance(lat1, lng1, lat2, lng2)
            if d < max_dist:
                return True

    return False

if __name__ == '__main__':

    # load configuration
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('./config.properties')
    bot = LikeFollowersBot(config)
    api = bot.login_to_instagram()

    if not api.isLoggedIn:
        bot.write_log("LOGIN ERROR" + str(bot.account_username) + "/" +  str(bot.account_password))
        quit()
    list = ["mattia+chiarini"]
    with open('nomi.csv') as f:
        cf = csv.reader(f)
        for row in cf:
            if len(row) > 0:
                n = row[0]
                list.append(n.replace(" ", "+").replace(".", "+"))

    print (list)


    header = ["chiave di ricerca","username", "full_name", "privato"]
    caption_valide = ['Bologna', 'BOLO']
    date_n_days_ago = datetime.now() - timedelta(100) # dieci giorni indietro
    min_timestamp = int(date_n_days_ago.strftime("%s"))
    max_media_loaded_by_user = 100

    # max a trenta km dal centro bologna
    lat1 = 44.5059073
    lng1 = 11.3411807
    max_dist = 20

    with open('./username_alievi.csv', 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(header)

        for l in list:
            res = api.fbUserSearch(l)
            #bot.write_log("SEARCH DONE: " + str(res))
            bot.write_log(api.LastJson)
            users = api.LastJson['users']
            for u in users:
                username_id = u['user']["pk"]
                username_ = u['user']['username']
                full_name_ = u['user']['full_name']
                private_ = u['user']['friendship_status']['is_private']
                row = [l, username_.encode('utf-8').strip(), full_name_.encode('utf-8').strip(), private_]
                if private_ is None or private_ == True:
                    continue

                ck = checkInteresting(bot, username_id, max_media_loaded_by_user, min_timestamp, caption_valide, lat1, lng1, max_dist)
                if not ck:
                    continue

                bot.write_log(str(row))
                wr.writerow(row)
            time_sleep = bot.bot_sleep()

    quit()

