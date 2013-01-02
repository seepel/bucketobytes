from twython import Twython, TwythonError
import threading
import pprint
import post
import time

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


class Stream(threading.Thread):
  def __init__(self, api, data, controllers=[], time_to_sleep=60, simulate=False):
    threading.Thread.__init__(self)
    self.api = api
    self.postQueue = post.PostQueue(api, simulate, controllers, time_to_sleep)
    self.postQueue.start()
    self.setDaemon(True)
    self.streamData = data
    self.retry_connection_in = 0
    self.pp = pprint.PrettyPrinter(depth=6)
    self.simulate = simulate


  def connectStream(self): 
    print 'connect'
    while True:
      print 'reconnect'
      try:
#        raise ValueError("Test Error")
        if self.simulate:
          print 'simulate'
          time.sleep(100)
        else:
          print 'really connect'
          self.api.stream(self.streamData, self.handle_results)
      except TwythonError:
        self.api.updateStatus(status='I crashed!')
        exit()
      except KeyboardInterrupt:
        print 'Exiting'
        exit()
#      except:
#        print 'Caught some other exception' 
#        self.retry_connection_in += 0.25
      print 'Retrying connection in ' + str(self.retry_connection_in) + 's'
      time.sleep(self.retry_connection_in)

  def handle_results(self, results):
    self.pp.pprint(results)
    if isinstance(results, (int, long)):
      print 'Recieved status: ' + str(results)
      if twitter_http_status_codes.has_key(results) and results != 420 and results < 500:
        status = twitter_http_status_codes[results][0] + ': ' + twitter_http_status_codes[results][1]
        if results != 401:
          remaining_len = 140 - len('@seepel I crashed: ')
          if len(status) > remaining_len:
            status = status[0:remaining_len]
          self.api.updateStatus(status='@seepel I crashed: ' + status)
        exit()
      if self.retry_connection_in == 0:
        if results == 420:
          self.retry_connection_in = 1
        else:
          self.retry_connection_in = 5
      else:
        if results == 420:
          self.retry_connection_in *= 2
        else:
          if self.retry_connection_in < 320:
            self.retry_connection_in *= 2
      return
    self.postQueue.queue.put(results)
    self.retry_connection_in = 0
  
