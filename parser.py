#!/usr/bin/python
import json
import sqlite3
import os
import os.path
import sys


class LogParser:
	def __init__(self, config):
		self.my_id = config['user_id']
		self.db = sqlite3.connect(config['database_path'])
		self.log_path = config['log_path']
		self.user_cache = {}


	def init_db(self):
		with open('setup.sql', 'r') as f:
			sql = f.read()
		c = self.db.executescript(sql)
		c.close()
		self.db.commit()


	def get_last(self):
		c = self.db.execute('select last_event_date, last_event_num from meta')
		res = c.fetchone()
		c.close()
		return res

	def set_last(self, filename, num):
		c = self.db.execute('update meta set last_event_date = ?, last_event_num = ?', (filename, num))
		c.close()


	def poke_user(self, user, field, check=None):
		uid = user['id']
		name = user['screen_name']

		if check:
			if uid in check:
				return
			check.add(uid)

		if uid not in self.user_cache:
			c = self.db.execute('select screen_name from users where user_id = ?', (uid,))
			row = c.fetchone()
			c.close()
			if row:
				self.user_cache[uid] = row[0]
			else:
				c = self.db.execute('insert into users (user_id, screen_name, %s) values (?, ?, 1)' % field, (uid, name))
				c.close()
				return

		if self.user_cache[uid] == name:
			c = self.db.execute('update users set %s = %s + 1 where user_id = ?' % (field, field), (uid,))
		else:
			print('username change detected: %s -> %s' % (self.user_cache[uid], name))
			self.user_cache[uid] = name
			c = self.db.execute('update users set %s = %s + 1, screen_name = ? where user_id = ?' % (field, field), (uid, name))
		c.close()


	def handle_fav(self, blob):
		source = blob['source']
		target = blob['target']
		if source['id'] == self.my_id:
			self.poke_user(target, 'favs_given')
		else:
			self.poke_user(source, 'favs_received')


	def handle_quote(self, blob):
		self.poke_user(blob['source'], 'quotes_received')


	def handle_my_tweet(self, blob):
		if 'retweeted_status' in blob:
			self.poke_user(blob['retweeted_status']['user'], 'rts_given')
		else:
			check = set()
			for mention in blob['entities']['user_mentions']:
				self.poke_user(mention, 'mentions_given', check)


	def handle_other_tweet(self, blob):
		if 'retweeted_status' in blob:
			if blob['retweeted_status']['user']['id'] == self.my_id:
				self.poke_user(blob['user'], 'rts_received')
			else:
				self.poke_user(blob['user'], 'tweets_seen')
		else:
			includes_me = False
			for mention in blob['entities']['user_mentions']:
				if mention['id'] == self.my_id:
					includes_me = True
			if includes_me:
				self.poke_user(blob['user'], 'mentions_received')
			else:
				self.poke_user(blob['user'], 'tweets_seen')


	def handle(self, timestamp, blob):
		if 'event' in blob:
			event = blob['event']
			if event == 'favorite':
				self.handle_fav(blob)
			elif event == 'quoted_tweet':
				self.handle_quote(blob)
		elif 'in_reply_to_status_id' in blob:
			if blob['user']['id'] == self.my_id:
				self.handle_my_tweet(blob)
			else:
				self.handle_other_tweet(blob)


	def process_new(self):
		event_count = 0
		file_count = 0

		logs = os.listdir(self.log_path)
		logs.sort()

		start_file, start_num = self.get_last()
		if start_file:
			logs = logs[logs.index(start_file):]
		
		for filename in logs:
			file_count += 1

			with open(os.path.join(self.log_path, filename), 'r') as f:
				lines = f.readlines()

			index = 0
			last_read = None
			if filename == start_file and start_num > 0:
				index = start_num + 1
				lines = lines[index:]

			for line in lines:
				if not line.endswith('\n'):
					break

				pipe = line.index('|')
				timestamp = float(line[:pipe])
				blob = json.loads(line[pipe+1:])
				self.handle(timestamp, blob)

				event_count += 1

				last_read = index
				index += 1

			self.set_last(filename, last_read)
			self.db.commit()

		return (file_count, event_count)




if len(sys.argv) != 3:
	print('usage: %s config.json [init|update]\n\t(or other filename)' % sys.argv[0])
else:
	_, config_path, command = sys.argv
	with open(config_path, 'r') as f:
		config = json.load(f)

	parser = LogParser(config)
	if command == 'init':
		parser.init_db()
		print('database reset')
	elif command == 'update':
		file_count, event_count = parser.process_new()
		print('%d event(s) in %d file(s) processed' % (event_count, file_count))
	else:
		print('unknown command')

