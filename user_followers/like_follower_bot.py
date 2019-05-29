#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Use text editor to edit the script and type in valid Instagram username/password
import sys

sys.path.insert(0, '../InstagramAPI')

from InstagramAPI import InstagramAPI
# import ConfigParser
import json
import os
import time
import logging
import random
from datetime import datetime, timedelta
from random import shuffle


class LikeFollowersBot:

    def __init__(self, config):
        self.config = config
        self.api = None

        # log
        self.log_mod = int(self.config.get("LOG", "log_mod"))
        self.log_dir_path = self.config.get("LOG", "log_dir_path")
        self.log_file_name = self.config.get("LOG", "log_file_name")
        self.log_file_path = os.path.join(self.log_dir_path, self.log_file_name)
        if not os.path.exists(self.log_dir_path):
            os.makedirs(self.log_dir_path)
        now_time = datetime.now()
        self.log_full_path = '%s_%s.log' % (self.log_file_path, now_time.strftime("%d.%m.%Y_%H:%M"))
        formatter = logging.Formatter('%(asctime)s - %(name)s ' '- %(message)s')
        self.logger = logging.getLogger('like_follower_bot')
        self.hdrl = logging.FileHandler(self.log_full_path, mode='a')
        self.hdrl.setFormatter(formatter)
        self.logger.setLevel(level=logging.INFO)
        self.logger.addHandler(self.hdrl)

        # ACCOUNT
        self.account_username = self.config.get("ACCOUNT", "username")
        self.account_password = self.config.get("ACCOUNT", "password")

        # DATABASE
        self.follower_dir_path = config.get("DATABASE", "follower_dir_path")
        if not os.path.exists(self.follower_dir_path):
            os.makedirs(self.follower_dir_path)
        self.follower_already_stored_file_path = config.get("DATABASE", "follower_already_stored_file_path")

        if not os.path.exists(self.follower_already_stored_file_path):
            self.reset_file(self.follower_already_stored_file_path)
        # if not reset_follower_already_stored_file:
        #    self.write_log("Error reset file " + str(self.follower_already_stored_file_path))

        self.follower_stored_dir_path = config.get("DATABASE", "follower_stored_dir_path")
        if not os.path.exists(self.follower_stored_dir_path):
            os.makedirs(self.follower_stored_dir_path)

        self.media_liked_dir_path = config.get("DATABASE", "media_liked_dir_path")
        if not os.path.exists(self.media_liked_dir_path):
            os.makedirs(self.media_liked_dir_path)
        self.media_liked_already_file_path = config.get("DATABASE", "media_liked_already_file_path")
        if not os.path.exists(self.media_liked_already_file_path):
            self.reset_file(self.media_liked_already_file_path)
        # if not reset_media_liked_already_file_path:
        #    self.write_log("Error reset file " + str(self.media_liked_already_file_path))

        self.media_unliked_dir_path = config.get("DATABASE", "media_unliked_dir_path")
        if not os.path.exists(self.media_unliked_dir_path):
            os.makedirs(self.media_unliked_dir_path)

        self.media_unliked_already_file_path = config.get("DATABASE", "media_unliked_already_file_path")
        if not os.path.exists(self.media_unliked_already_file_path):
            self.reset_file(self.media_unliked_already_file_path)

        self.action_delay = int(config.get("TIME", "action_delay"))
        self.days_before = int(config.get("SEARCH", "days_before"))
        self.media_liked_scan_rate = int(config.get("SEARCH", "media_liked_scan_rate"))
        self.max_media_to_unlike = int(config.get("SEARCH", "max_media_to_unlike"))

        self.follower_store_deep = int(config.get("STORE", "follower_store_deep"))
        self.max_followers_loaded_by_user = int(config.get("STORE", "max_followers_loaded_by_user"))
        self.max_media_loaded_by_user = int(config.get("STORE", "max_media_loaded_by_user"))
        self.max_following_count = (int(config.get("STORE", "max_following_count")))
        self.max_follower_count = (int(config.get("STORE", "max_follower_count")))
        #

    def bot_sleep(self, delay_par=None):

        delay = delay_par
        if delay_par is None:
            delay = self.action_delay

        time_random = delay * 0.5 + delay * 0.5 * random.random()
        self.write_log("... sleeping for %d sec..." % time_random)
        time.sleep(time_random)
        return time_random

    def write_log(self, log_text):

        if self.log_mod == 0:
            try:
                self.pretty_print_log_text(log_text)
            except UnicodeEncodeError:
                print("Your text has unicode problem!")

        elif self.log_mod == 1:
            # Log to log file.
            try:
                self.logger.info(log_text)
            except UnicodeEncodeError:
                print("Your text has unicode problem!")
        elif self.log_mod == 2:
            # Log to log file.
            try:
                self.pretty_print_log_text(log_text)
                self.logger.info(log_text)
            except UnicodeEncodeError:
                print("Your text has unicode problem!")

    def pretty_print_log_text(self, log_text, size=60):
        now_time = datetime.now()
        str_now_time = now_time.strftime("%d.%m.%Y_%H:%M")
        log_text_trim = (log_text[:size] + '..') if len(log_text) > size else log_text
        print(str_now_time + " - " + str(log_text_trim))

    def login_to_instagram(self):

        self.write_log(self.account_username + "/" + self.account_password)
        self.api = InstagramAPI(self.account_username, self.account_password)
        self.api.login()
        return self.api

    def get_not_yet_liked_user_feed(self, username_id, max_media_loaded_by_user, minTimestamp=None):
        feeds = self.get_total_user_feed(username_id, max_media_loaded_by_user, minTimestamp)
        time_sleep = self.bot_sleep()
        self.write_log("INFO, ... sleep after loaded media: %d sec." % time_sleep)
        not_yet_liked = [i for i in feeds if i['has_liked'] is not None and i['has_liked'] is False]  # not liked
        return not_yet_liked


    def get_total_user_feed(self, username_id, max_media_loaded_by_user, minTimestamp=None):
        user_feed = []
        next_max_id = ''
        while len(user_feed) < max_media_loaded_by_user:
            getUserFeed = self.api.getUserFeed(username_id, next_max_id, minTimestamp)
            time.sleep(random.randint(0, 2))  # simulate a scroll app delay
            if not getUserFeed:
                self.write_log("ERROR, loading followers, userid: " + str(username_id) + " next_max_id: " + str(next_max_id))
                break

            temp = self.api.LastJson

            if 'items' not in temp:
                self.write_log("ERROR, loading followers, userid: " + str(username_id) + " response: " + str(temp))
                break

            for item in temp["items"]:
                user_feed.append(item)

            if temp["more_available"] is False:
                break

            next_max_id = temp["next_max_id"]

        return user_feed

    def get_total_followers(self, username_id, max_followers_loaded_by_user):
        followers = []
        next_max_id = ''

        while len(followers) < max_followers_loaded_by_user:
            self.api.getUserFollowers(username_id, next_max_id)
            # simulate a scroll app delay
            time.sleep(random.randint(0, 2))
            temp = self.api.LastJson

            if 'users' not in temp:
                self.write_log("ERROR, loading followers, userid: " + str(username_id) + " response: " + str(temp))
                break

            for item in temp["users"]:
                followers.append(item)

            if temp["big_list"] is False:
                break
            next_max_id = temp["next_max_id"]

        return followers

    def unlike_media(self, username_to_search):
        unlike_done = 0

        # load user info
        user_info = self.load_user_info(username_to_search)
        if user_info is None:
            return unlike_done
        all_liked_media = self.api.getTotalLikedMedia(self.media_liked_scan_rate)

        if all_liked_media is None or len(all_liked_media) == 0:
            self.write_log("WARN, NO loaded media for user: " + str(username_to_search))
            return unlike_done

        self.write_log("INFO, loaded media for user: " + str(username_to_search) +
                       " tot: " + str(len(all_liked_media)) + " media")

        shuffle(all_liked_media)

        # select first media to like

        for media_to_unlike in all_liked_media:
            if media_to_unlike is None:
                self.write_log("WARN, error media_to_unlike None for : " + str(username_to_search))
                continue

            # check owner is username_to_search
            if media_to_unlike['user']['username'] == username_to_search:
                continue

            if self.id_exist_in_file(media_to_unlike['pk'], self.media_unliked_already_file_path):
                self.write_log("INFO, media already unliked " + str(
                    media_to_unlike['caption']))  # + ", " + str(self.api.LastJson))
                continue

            unlike_action_result = self.api.unlike(media_to_unlike['pk'])
            time_sleep = self.bot_sleep()
            self.write_log("INFO, ... sleep after unlike: %d sec." % time_sleep)
            if unlike_action_result:
                self.write_log(
                    "INFO, unliked media " + str(media_to_unlike['caption']))  # + ", "+ str(self.api.LastJson))
                unlike_done = unlike_done + 1
                self.append_id_to_file(media_to_unlike['pk'], self.media_unliked_already_file_path)

            else:
                self.write_log("ERROR, no unliked media " + str(media_to_unlike['caption']) + ", "
                               + str(self.api.LastJson))
                if "Temporarily Blocked" in self.api.LastJson['feedback_title'] and "fail" in self.api.LastJson[
                    'status']:
                    raise Exception(" unlike Temporarily Blocked")
            if unlike_done > self.max_media_to_unlike:
                self.write_log("WARN, max unlike after stop: " + str(self.max_media_to_unlike))
                return unlike_done

        return unlike_done

    def like_follower_media_user_recursive(self, username_to_search, deep):

        if deep > self.follower_store_deep:
            return 0

        user_data = None

        try:
            user_data = self.load_user_data(username_to_search, load_media=False)
        except Exception as e:
            self.write_log("ERROR, load_user_data: " + str(username_to_search) + ", " + str(e))
            return 0

        followers = user_data['followers']
        if followers is None:
            self.write_log("ERROR, loading followers for data: " + str(user_data))
            return 0

        shuffle(followers)
        like_done_count = 0
        for follower in followers:
            follower_username = follower['username']
            if follower_username is None:
                self.write_log("ERROR, None username for data: " + str(user_data))
                continue
            try:
                like_done = self.like_first_media_user(follower_username)
                like_done_count = like_done_count+like_done
            except Exception as e:
                self.write_log("ERROR, like_first_media_user: " + str(follower_username) + ", " + str(e))
                continue

            try:
                like_done_deep = self.like_follower_media_user_recursive(follower_username, deep + 1)
                like_done_count = like_done_count + like_done_deep
            except Exception as e:
                self.write_log("ERROR, like_follower_media_user_recursive: " + str(follower_username) + ", " + str(e))


        return like_done_count



    def like_first_media_user(self, username):
        like_done = 0

        user_info = self.load_user_info(username)
        if user_info is None:
            return like_done

        user_pk = user_info['pk']

        if (user_info['follower_count']) > self.max_follower_count:
            self.write_log("WARN, TO MUCH FOLLOWER (" + str(user_info['follower_count']) + ") " + str(user_info['username']))
            return like_done

        if (user_info['following_count']) > self.max_following_count:
            self.write_log("WARN, TO MUCH FOLLOWING (" + str(user_info['following_count']) + ") " +str(user_info['username']))
            return like_done


        date_n_days_ago = datetime.now() - timedelta(days=self.days_before)
        min_timestamp = int(date_n_days_ago.strftime("%s"))
        not_yet_liked = self.get_not_yet_liked_user_feed(user_pk, self.max_media_loaded_by_user, minTimestamp=min_timestamp)
        if not_yet_liked is None:
            self.write_log("WARN, NO MEDIA TO LIKE FOR " + str(user_info['username']))
            return 0

        self.write_log("INFO, loaded media for user: " + str(user_info['username']) +
                       " tot: " + str(len(not_yet_liked)) + " media")

        # select first media to like
        media_to_like = None
        for media in not_yet_liked:
            if self.id_exist_in_file(media['pk'], self.media_liked_already_file_path):
                continue
            self.append_id_to_file(media['pk'], self.media_liked_already_file_path)
            media_to_like = media
            break

        if media_to_like is None:
            self.write_log("WARN, all media already liked for : " + str(user_info['username']))
            return like_done

        like_action_result = self.api.like(media_to_like['pk'])
        time_sleep = self.bot_sleep()
        self.write_log("INFO, ... sleep after like: %d sec." % time_sleep)
        if like_action_result:
            self.write_log("INFO, liked media " + str(media_to_like['caption']))
            like_done = 1
        else:
            self.write_log("ERROR, no liked media " + str(media_to_like['caption']) + ", "
                           + str(self.api.LastJson))
            if "fail" in self.api.LastJson['status'] and "Temporarily Blocked" in self.api.LastJson[
                'feedback_title']:
                raise Exception(" like Temporarily Blocked")

        return like_done

    def like_follower_media(self):
        like_done = 0
        only_files = [f for f in os.listdir(self.follower_dir_path) if
                      os.path.isfile(os.path.join(self.follower_dir_path, f)) and f.endswith(".json")]

        shuffle(only_files)
        for f in only_files:
            self.write_log("INFO, open file: " + str(f))

            with open(os.path.join(self.follower_dir_path, f)) as data_file:

                user_data = json.load(data_file)
                if user_data is None:
                    self.write_log("Error, loading user from file: " + str(f))
                    self.write_log(str(data_file))
                    continue

                feeds = user_data['medias']
                if feeds is None or len(feeds) == 0:
                    self.write_log("WARN, NO loaded media for user: " + str(user_data['user_info']['username']))
                    continue

                self.write_log("INFO, loaded media for user: " + str(user_data['user_info']['username']) +
                               " tot: " + str(len(feeds)) + " media")

                # select first media to like
                media_to_like = None
                for media in feeds:
                    if self.id_exist_in_file(media['pk'], self.media_liked_already_file_path):
                        continue
                    self.append_id_to_file(media['pk'], self.media_liked_already_file_path)
                    media_to_like = media
                    break

                if media_to_like is None:
                    self.write_log("WARN, all media already liked for : " + str(user_data['user_info']['username']))
                    continue

                like_action_result = self.api.like(media_to_like['pk'])
                time_sleep = self.bot_sleep()
                self.write_log("INFO, ... sleep after like: %d sec." % time_sleep)
                if like_action_result:
                    self.write_log("INFO, liked media " + str(media_to_like['caption']))
                    like_done = like_done + 1
                else:
                    self.write_log("ERROR, no liked media " + str(media_to_like['caption']) + ", "
                                   + str(self.api.LastJson))
                    if "fail" in self.api.LastJson['status'] and "Temporarily Blocked" in self.api.LastJson[
                        'feedback_title']:
                        raise Exception(" like Temporarily Blocked")

        return like_done

    def load_user_data(self, username_to_search, load_media=True):

        user_data = {}

        # load user info
        user_info = self.load_user_info(username_to_search)
        if user_info is None:
            return None

        self.write_log("INFO, loaded : " + str(username_to_search) + ", id: " + str(user_info['pk']))
        user_data['user_info'] = user_info

        user_pk = user_info['pk']
        id_exist_in_file = self.id_exist_in_file(user_pk, self.follower_already_stored_file_path)
        user_data["already_stored"] = id_exist_in_file

        # load followers
        search_user_followers = self.get_total_followers(user_pk, self.max_followers_loaded_by_user)
        self.write_log("INFO, loaded followers " + str(user_info['username']) + " tot: "
                       + str(len(search_user_followers)) + " follower")
        time_sleep = self.bot_sleep()
        self.write_log("INFO, ... sleep after loaded followers: %d sec." % time_sleep)

        # filter no private and not verified
        filtered_search_user_followers = [item for item in search_user_followers if
                                          item['is_private'] is False and item['is_verified'] is False]

        # shuffle(filtered_search_user_followers)
        user_data['followers'] = filtered_search_user_followers

        # load media not already liked
        if load_media and not id_exist_in_file:

            date_n_days_ago = datetime.now() - timedelta(days=self.days_before)
            min_timestamp = int(date_n_days_ago.strftime("%s"))
            feeds = self.get_total_user_feed(user_pk, self.max_media_loaded_by_user, minTimestamp=min_timestamp)
            self.write_log("INFO, loaded media for user: " + str(user_info['username']) + "tot: " + str(len(feeds))
                           + " media")
            time_sleep = self.bot_sleep()
            self.write_log("INFO, ... sleep after loaded media: %d sec." % time_sleep)
            not_yet_liked = [i for i in feeds if i['has_liked'] is not None and i['has_liked'] is False]  # not liked
            if not_yet_liked is None:
                self.write_log("WARN, NO MEDIA TO LIKE FOR " + str(user_info['username']))
            user_data['medias'] = not_yet_liked
        else:
            user_data['medias'] = None

        return user_data

    def load_user_info(self, username_to_search):
        search_username = self.api.searchUsername(username_to_search)
        time_sleep = self.bot_sleep()
        self.write_log("INFO, ... sleep after loading user info: %d sec." % time_sleep)
        if not search_username:
            self.write_log("ERROR, search follower from " + str(username_to_search))
            return None
        if self.api.LastJson is None:
            self.write_log("ERROR, search json follower from " + str(username_to_search))
            return None
        user_info = self.api.LastJson['user']
        return user_info

    def store_all_follower_info(self, username_to_search):
        stored = 0
        user_data = self.load_user_data(username_to_search, load_media=False)
        if user_data is None:
            self.write_log("ERROR, No data while loading root user " + str(username_to_search) + " PROCESS STOP!!!")
            return

        if not user_data["already_stored"]:
            file_path = os.path.join(self.follower_dir_path, username_to_search + '.json')
            with open(file_path, 'w') as outfile:
                json.dump(user_data, outfile)
                outfile.close()
                stored = stored + 1
        stored = stored + self.store_all_follower_info_recursive(user_data, 1)
        return stored

    def store_all_follower_info_recursive(self, user_data, deep):
        if deep > self.follower_store_deep:
            return 0

        if user_data is None:
            self.write_log("ERROR, empty user_data")
            return 0

        followers = user_data['followers']
        if followers is None:
            self.write_log("ERROR, loading followers for data: " + str(user_data))
            return 0

        shuffle(followers)

        stored = 0
        for follower in followers:
            follower_username = follower['username']
            if follower_username is None:
                self.write_log("ERROR, None username for data: " + str(user_data))
                continue

            try:
                user_data = self.load_user_data(follower_username, load_media=True)
                if user_data is None:
                    self.write_log("ERROR, No data while loading follower: " + str(follower_username))
                    continue
                if not user_data["already_stored"]:
                    user_pk = user_data['user_info']['pk']
                    self.append_id_to_file(user_pk, self.follower_already_stored_file_path)
                    file_path = os.path.join(self.follower_dir_path, follower_username + '.json')
                    with open(file_path, 'w') as outfile:
                        json.dump(user_data, outfile)
                        outfile.close()
                        stored = stored + 1

                stored = stored + self.store_all_follower_info_recursive(user_data, deep + 1)
            except Exception as e:
                self.write_log("ERROR, loading data follower: " + str(follower_username) + ", " + str(e))

        return stored

    def id_exist_in_file(self, par_id, file_path):
        search = str(str(par_id) + '\n')
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if search == line:
                        return True

        except IOError as e:
            self.write_log("Unable to open file " + str(file_path) + ", " + str(e))
            with open(file_path, 'w') as f:
                f.write("LIST \n")

        return False

    def append_id_to_file(self, par_id, file_path):
        try:
            with open(file_path, "a") as f:
                f.write(str(par_id) + "\n")
                return True

        except IOError as e:
            self.write_log("Unable to open file " + str(file_path) + ", " + str(e))
            with open(file_path, 'w') as f:
                f.write("LIST \n")
                f.write(str(par_id) + "\n")

        return False

    def reset_file(self, file_path):
        if not os.path.exists(file_path):
            try:
                with open(file_path, "a") as f:
                    f.write("LIST \n")
                    return True

            except IOError as e:
                self.write_log("Unable to open file " + str(file_path) + ", " + str(e))
        else:
            os.remove(file_path)
            try:
                with open(file_path, "w") as f:
                    f.write("LIST \n")
                    return True

            except IOError as e:
                self.write_log("Unable to open file " + str(file_path) + ", " + str(e))

        return False
