import post
from datetime import datetime

class ReplyController(post.PostController):
  def __init__(self, post_composers = [], postControllers = None, current_user=None):
    post.PostController(post_composers, postControllers, current_user)
    self.post_composers = post_composers
    self.current_user = current_user
    self.reply_ids = { }

  def can_handle_object(self, post_object):
    if self.isCurrentUser(post_object):
      return False
    if not post_object.has_key('entities'):
      return False
    if not post_object['entities'].has_key('user_mentions'):
      return False
    if post_object.has_key('retweeted_status'):
      return False
    for user_mention in post_object['entities']['user_mentions']:
      if user_mention['id_str'] == self.current_user['id_str']:
        return True
    return False

  def probabilityToPost(self, post_object, seconds_from_midnight, time_step, simulate=False):
    if self.isCurrentUser(post_object):
      return 0
    if not post_object.has_key('entities'):
      return 0
    if not post_object['entities'].has_key('user_mentions'):
      return 0
    if post_object.has_key('retweeted_status'):
      return 0
    for user_mention in post_object['entities']['user_mentions']:
      if user_mention['id_str'] == self.current_user['id_str']:
        return self.probabilityForId(post_object, seconds_from_midnight, time_step)
    return 0

  def probabilityForId(self, post_object, seconds_from_midnight, time_step):
    if not post_object.has_key('user'):
      return 0
    if not post_object['user'].has_key('id_str'):
      return 0
    user_id = post_object['user']['id_str']
    if not self.reply_ids.has_key(user_id):
      self.reply_ids[user_id] = { 'probability' : 1, 'first_reply' : datetime.today(), 'last_attempt' : datetime.min }

    current_datetime = datetime.today()
    if (current_datetime - self.reply_ids[user_id]['first_reply']).seconds > 1:#60*60*24:
      self.reply_ids[user_id] = { 'probability' : 1, 'first_reply' : datetime.today(), 'last_attempt' : datetime.min }
      return 1

    probability = self.reply_ids[user_id]['probability']
    delta = (datetime.today() - self.reply_ids[user_id]['last_attempt'])
    if delta.microseconds < 500:
      probability = 0

    self.reply_ids[user_id]['last_attempt'] = datetime.today()

    return probability

  def postUpdateStatus(self, api, post_object):
    user_id = post_object['user']['id_str']
    probability = float(self.reply_ids[user_id]['probability'])
    self.reply_ids[user_id]['probability'] = probability * 0.5
