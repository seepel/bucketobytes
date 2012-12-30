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

fortunes = open('fortunes').read().split('\n%\n')
if len(fortunes) == 0:
  exit()

for fortune in fortunes:
  if len(fortune) > 140:
    fortunes.remove(fortune)

while True:
  fortune = random.choice(fortunes)
  api.updateStatus(status=fortune)
  print fortune
  time.sleep(random.randrange(2700,4500,1))

