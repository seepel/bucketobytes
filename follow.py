from twython import Twython
import post

class FollowController(post.PostController):
  def __init__(self, post_composers = [], postControllers = None, current_user=None):
    post.PostController(post_composers, postControllers, current_user)
    self.post_composers = post_composers
    self.current_user = current_user

  def can_handle_object(self, post_object):
    if not post_object.has_key('event'):
      return False
    if post_object['event'] != 'follow':
      return False
    return True

  def probabilityToPost(self, post_object, seconds_from_midnight, time_step, simulate=False):
    if not post_object.has_key('event'):
      return 0
    if post_object['event'] != 'follow':
      return 0
    return 1

class FollowComposer(post.PostComposer):
  def __init__(self, current_user):
    self.current_user = current_user

  def compose(self, api, post_object, simulate):
    if not post_object.has_key('source'):
      return None
    if not post_object.has_key('target'):
      return None

    user_to_follow = None
    if post_object['source']['id_str'] != self.current_user['id_str']:
      user_to_follow = post_object['source']['id_str']
    if post_object['target']['id_str'] != self.current_user['id_str']:
      user_to_follow = post_object['target']['id_str']
    if user_to_follow == None:
      return None
    if simulate:
      return 'Follow -> ' + user_to_follow
    else:
      return api.createFriendship(user_id=user_to_follow)
