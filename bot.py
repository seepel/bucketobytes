from twython import Twython, TwythonError
from optparse import OptionParser
import os
import random
import pprint
import time
import post
import reply
import retweet
import stream
from fortune import FortuneComposer
import simulate
import follow

twitter_http_status_codes = {
    200: ('OK', 'Success!'),
    304: ('Not Modified', 'There was no new data to return.'),                            
    400: ('Bad Request', 'The request was invalid. An accompanying error message will explain why. This is the status code will be returned during rate limiting.'),
    401: ('Unauthorized', 'Authentication credentials were missing or incorrect.'),       
    403: ('Forbidden', 'The request is understood, but it has been refused. An accompanying error message will explain why. This code is used when requests are being denied due to update limits.'),
    404: ('Not Found', 'The URI requested is invalid or the resource requested, such as a user, does not exists.'),
    406: ('Not Acceptable', 'Returned by the Search API when an invalid format is specified in the request.'),
    420: ('Enhance Your Calm', 'Returned by the Search and Trends API when you are being rate limited.'),
    500: ('Internal Server Error', 'Something is broken. Please post to the group so the Twitter team can investigate.'),
    502: ('Bad Gateway', 'Twitter is down or being upgraded.'),                           
    503: ('Service Unavailable', 'The Twitter servers are up, but overloaded with requests. Try again later.'),
}


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

#do_simulate = True
do_simulate = False

current_user = { 'id_str' : '1041065317' }
if not do_simulate:
  current_user = api.verifyCredentials()
  pp.pprint(current_user)

fortuneComposer = FortuneComposer()
followController = follow.FollowController([ follow.FollowComposer(current_user) ], current_user=current_user)
retweetController = retweet.RetweetController([ retweet.RetweetComposer() ], current_user=current_user)
replyController = reply.ReplyController([ fortuneComposer ], current_user=current_user)
postController = post.PostController([ fortuneComposer ], current_user=current_user)
default_time_to_sleep = 1
if do_simulate:
  default_time_to_sleep = 1

user_stream = stream.Stream(api, 
                            { 'endpoint' : 'https://userstream.twitter.com/1.1/user.json', 'track' : 'bucketobytes' }, 
                            [ followController, retweetController, replyController, postController ],
                            default_time_to_sleep,
                            do_simulate)
#for i in range(20):
#  for mention in simulate.mentions:
#    user_stream.postQueue.queue.put(mention)

user_stream.connectStream()
