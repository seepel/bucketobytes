from twython import Twython, TwythonError
from optparse import OptionParser
import os
import random
import pprint
import time

parser = OptionParser()
parser.add_option('--consumer_key', dest='consumer_key')
parser.add_option('--consumer_secret', dest='consumer_secret')
parser.add_option('--access_token_key', dest='access_token_key')
parser.add_option('--access_token_secret', dest='access_token_secret')
(options, args) = parser.parse_args()

if options.consumer_key == None:
  print "No consumer key"
  exit()

if options.consumer_secret == None:
  print "No consumer secret"
  exit()

if options.access_token_key == None:
  print "No access_token key"
  exit()

if options.consumer_key == None:
  print "No consumer key"
  exit()

pp = pprint.PrettyPrinter(depth=6)

api = Twython(app_key=options.consumer_key,
              app_secret=options.consumer_secret,
              oauth_token=options.access_token_key,
              oauth_token_secret=options.access_token_secret)

rates = api.getRateLimitStatus()
remaining_hits = rates['remaining_hits']
rate_reset = rates['reset_time_in_seconds']
print 'Rate limit: ' + str(remaining_hits)

current_user = api.verifyCredentials()

fortunes = open('fortunes').read().split('\n%\n')
if len(fortunes) == 0:
  exit()

for fortune in fortunes:
  if len(fortune) > 140:
    fortunes.remove(fortune)

def followed(follow):
  source_id = follow['source']['id_str']
  target_id = follow['target']['id_str']
  new_id = ""
  if source_id != current_user['id_str']:
    new_id = source_id
  elif target_id != current_user['id_str']:
    new_id = target_id
    
  print 'FRIEND: ' + new_id
  api.createFriendship(user_id=new_id)

def cc(status):
  api.reTweet(id=status['id_str'])
  remaining_hits = remaining_hits-1

def reply(status):
  user = status['user']['id_str']
  max_length = 140 - len(user)-2
  content = random.choice(fortunes)
  count = 0
  while len(content) > max_length:
    if count > 1000:
      break
    content = random.choice(fortunes)
  content = '@' + status['user']['screen_name'] + ' ' + content
  print content
  api.updateStatus(status=content, in_reply_to_status_id=status['id_str'])
  remaining_hits = remaining_hits-1

def mentioned(status):
  if '#cc' in status['text']:
    cc(status)
  else:
    reply(status)


def on_results(results):
  global rate_reset
  global remaining_hits
  pp.pprint(results)
  if remaining_hits <= 0:
    print "hit my limit!"
    return
  if time.gmtime() > rate_reset:
    rates = api.getRateLimitStatus()
    remaining_hits = rates['remaining_hits']
    rate_reset = rates['reset_time_in_seconds']
    print 'Rate limit: ' + str(remaining_hits)
  try:
    if results.has_key('event'):
      if results['event'] == 'follow':
        followed(results)
    elif results.has_key('entities'):
        return
      if results['user']['id_str'] == current_user['id_str']:
        return
      if results['entities'].has_key('user_mentions'):
        for user_mention in results['entities']['user_mentions']:
          if user_mention['id_str'] == current_user['id_str']:
            mentioned(results)
            break
  except TwythonError:
    api.updateStatus(status='@seepel I encountered an error!')

try:
  api.stream({ 'endpoint' : 'https://userstream.twitter.com/1.1/user.json' }, on_results)
except TwythonError:
  api.updateStatus(status='@seepel I have crashed!')
