import twitter
from optparse import OptionParser
import os
import random

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

api = twitter.Api(consumer_key=options.consumer_key,
                  consumer_secret=options.consumer_secret,
                  access_token_key=options.access_token_key,
                  access_token_secret=options.access_token_secret)
#print api.VerifyCredentials()


#for status in api.GetUserTimeline('bucketobytes')

fortunes = open('fortunes').read().split('\n%\n')
if len(fortunes) == 0:
  exit()

followers = api.GetFollowerIDs()[u'ids']
following = api.GetFriendIDs()[u'ids']
for  follower in followers:
  if follower not in following:
    api.CreateFriendship(follower)

last_reply = None
if os.path.exists('last_reply'):
  last_reply_file = open('last_reply', 'r')
  last_reply = last_reply_file.read()
  last_reply_file.close()
  os.remove('last_reply')

mentions = None

if last_reply != None and last_reply != "":
  mentions = api.GetMentions(since_id=last_reply)
else:
  mentions = api.GetMentions()

for status in reversed(mentions):
  user = status.user.screen_name
  max_length = 140 - len(user)-2
  content = random.choice(fortunes)
  count = 0
  while len(content) > max_length:
    if count > 1000:
      break
    content = random.choice(fortunes)
  print content
  api.PostUpdate(u'@'+unicode(user)+u' '+unicode(content), in_reply_to_status_id=status.id)
  last_reply = status.id

last_reply_file = open('last_reply', 'w')
last_reply_file.write(str(last_reply))
last_reply_file.close()

for fortune in fortunes:
  if len(fortune) > 140:
    fortunes.remove(fortune)

content = random.choice(fortunes)

if content != None and content != "":
  status = api.PostUpdate(content)
  print status.text
