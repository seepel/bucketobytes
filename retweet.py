from post import PostComposer
import reply

class RetweetController(reply.ReplyController):
  def __init__(self, post_composers = [], postControllers = None, current_user=None):
    reply.ReplyController(post_composers, postControllers, current_user)
    self.post_composers = post_composers
    self.current_user = current_user
    self.reply_ids = { }
    self.retweets = [ ]

  def can_handle_object(self, post_object):
    if not post_object.has_key('text'):
      return False
    if not '#cc' in post_object['text']:
      return False
    if post_object['text'] in self.retweets:
      return False
    return True

  def probabilityToPost(self, post_object, seconds_from_midnight, time_step, simulate=False):
    if not post_object.has_key('text'):
      return 0
    if not '#cc' in post_object['text']:
      return 0
    if post_object['text'] in self.retweets:
      return 0
    return reply.ReplyController.probabilityToPost(self, post_object, seconds_from_midnight, time_step, simulate)

  def postUpdateStatus(self, api, post_object):
    self.retweets.append(post_object['text'])
    reply.ReplyController.postUpdateStatus(self, api, post_object)

class RetweetComposer(PostComposer):
  def __init__(self):
    PostComposer()

  def compose(self, api, post_object, simulate):
    if not post_object.has_key('id_str') or not post_object.has_key('text'):
      return None
    if simulate:
      return 'RETWEET: ' + post_object['text']
    return api.reTweet(id=post_object['id_str'])
