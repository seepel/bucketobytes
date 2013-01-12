from twython import Twython
import threading
import Queue
import pprint
from apscheduler.scheduler import Scheduler
import time
import random

from datetime import datetime

class PostComposer(object):
  def __init__(self):
    pass

  def compose(self, api, post_object):
    return None

  def percent(self):
    return 100

class PostController(object):
  def __init__(self, post_composers = [], postControllers = None, current_user=None):
    self.post_composers = post_composers
    self.current_user = current_user

  def can_handle_object(self, post_object):
    return len(post_object) == 0

  def probabilityToPost(self, post_object, seconds_from_midnight, time_step, simulate=False):
    if len(post_object) != 0:
      return 0
    if self.isCurrentUser(post_object):
      return 0
    # flat distribution 22 tweets per day
    one_day = 60.*60.*24./float(time_step)
    if simulate:
      one_day /= 60
    return 12./one_day

  def isCurrentUser(self, post_object):
    if self.current_user == None:
      print 'No current user skipping'
      return False
    # don't respond if the tweet belongs to the current user -- would be infinite loop!
    if post_object.has_key('user'):
      if post_object['user'].has_key('id_str'):
        return post_object['user']['id_str'] == self.current_user['id_str']
    return False

  def choosePostComposer(self):
    post_composers = []
    total_percent = 0
    for post_composer in self.post_composers:
      if post_composer.percent() == 100:
        return post_composer
      post_composers.append(post_composer)
      total_percent += post_composer.percent()
    probability = random.randrange(total_percent)
    threshold = 0
    for post_composer in post_composers:
      if threshold <= post_composer.percent():
        return post_composer
      threshold += post_composer.percent()
    return post_composer

  def composePost(self, api, post_object, simulate):
    return self.choosePostComposer().compose(api, post_object, simulate)

  def postUpdateStatus(self, api, post_object):
    pass


class PostScheduler(threading.Thread):
  def __init__(self, api, simulate=False, controllers=None, default_time_to_sleep=60):
    threading.Thread.__init__(self)
    self.scheduler = Scheduler()
    self.scheduler.start()
    self.api = api
    self.simulate = simulate
    self.controllers = controllers
    self.queue = Queue.Queue()
    self.post_objects = []
    self.default_time_to_sleep = default_time_to_sleep
    self.count = 0
    self.posts = 0
    self.setDaemon(True)

  def run(self):
    while True:
      queue_object = self.queue.get()
      
      if self.queue.empty():
        self.queue.put(self.default_time_to_sleep)

      if isinstance(queue_object, (int, long, float)):
        if self.count > 0 and self.count % (60*24) == 0 and self.simulate:
          print '====================== DAY ' + str(self.count/60/24) + ' -> ' + str(self.posts) + ' in queue: ' + str(len(self.post_objects)) + ' ========================'
          self.posts = 0
        time_to_sleep = queue_object
        if time_to_sleep > 0:
          time.sleep(time_to_sleep)
          self.evaluate_tweets()
      else:
        self.post_objects.append(queue_object)

      self.queue.task_done()


  def evaluate_tweets(self):
    self.count += 1
    seconds_from_midnight = (datetime.today() - datetime.min).seconds
    post_objects_to_remove = []

    for post_object in self.post_objects:
      can_be_handled = False
      for controller in self.controllers:
        if controller.can_handle_object(post_object):
          can_be_handled = True
          break
      if not can_be_handled:
        post_objects_to_remove.append(post_object)

    for post_object in post_objects_to_remove:
      self.post_objects.remove(post_object)

    for controller in self.controllers:
      chosen_object = None
      for post_object in self.post_objects:
        if self.evaluate_tweet(controller, post_object, seconds_from_midnight):
          chosen_object = post_object
          break
      if chosen_object != None:
        self.post_objects.remove(chosen_object)
        break
      self.evaluate_tweet(controller, { }, seconds_from_midnight)

  def evaluate_tweet(self, controller, post_object, seconds_from_midnight):
    probability = controller.probabilityToPost(post_object, seconds_from_midnight, self.default_time_to_sleep, self.simulate)
    if probability == 0:
      return False
    steps = 10000.0
    random_number = random.randrange(steps)/steps
    if random_number <= probability:
      self.posts += 1
      print controller
      print controller.composePost(self.api, post_object, self.simulate)
      controller.postUpdateStatus(self.api, post_object)
      return True
    return False

class PostQueue(threading.Thread):
  def __init__(self, api, simulate=False, controllers=None, default_time_to_sleep=60):
    threading.Thread.__init__(self)
    self.postScheduler = PostScheduler(api, simulate, controllers, default_time_to_sleep)
    self.queue = Queue.Queue()
    self.postScheduler.start()
    self.postScheduler.queue.put(0)
    self.setDaemon(True)

  def run(self):
    while True:
      post_object = self.queue.get()
      self.postScheduler.queue.put(post_object)
      self.queue.task_done()


