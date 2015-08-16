#!/usr/bin/env python
from twitter import TwitterStream, OAuth
import time
import json
import os
import os.path
import sys


class Logger:
	def __init__(self, path):
		self.cur_date = None
		self.cur_file = None
		self.path = path
		try:
			os.makedirs(path)
		except OSError:
			# assume this is "File exists" for the time being :p
			pass

	def log(self, blob):
		unix = time.time()
		date_str = time.strftime('%Y-%m-%d', time.gmtime(unix))
		if date_str != self.cur_date:
			self.cur_date = date_str
			if self.cur_file:
				self.cur_file.close()

			path = os.path.join(self.path, '%s.log' % date_str)
			self.cur_file = open(path, 'a')

		self.cur_file.write('%d|%s\n' % (unix, blob))
		self.cur_file.flush()


def run(config, verbose=True):
	uid = config['user_id']
	auth = OAuth(
			config['token'], config['token_secret'],
			config['consumer_key'], config['consumer_secret'])

	log = Logger(config['log_path'])
	print('connecting %d...' % uid)
	stream = TwitterStream(domain='userstream.twitter.com', auth=auth)
	for obj in stream.user():
		if verbose:
			if 'event' in obj:
				print('event: %s' % obj['event'])
			elif 'in_reply_to_status_id' in obj:
				print('tweet by %s' % obj['user']['screen_name'])
			elif 'friends' in obj:
				print('friends list obtained, streaming begins')
			else:
				print(repr(obj))

		log.log(json.dumps(obj))

	print('connection lost for %d' % uid)


if len(sys.argv) != 2:
	print('usage: %s config.json\n\t(or other filename)' % sys.argv[0])
else:
	with open(sys.argv[1], 'r') as f:
		config = json.load(f)
	run(config)

