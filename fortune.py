from post import PostComposer
import random

fortunes = open('fortunes').read().split('\n%\n')

class FortuneComposer(PostComposer):
  def __init__(self):
    self.fortunes = fortunes
    for fortune in self.fortunes:
      if len(fortune) > 140:
        self.fortunes.remove(fortune)

  def compose(self, api, post_object, simulate):
    fortune = None
    screen_name = None
    if post_object.has_key('user'):
      if post_object['user'].has_key('screen_name'):
        screen_name = post_object['user']['screen_name']
    if screen_name != None:
      fortune = self.chooseFortune(140, screen_name)
    else:
      fortune = self.chooseFortune()
    if fortune == None:
      return None
    if simulate:
      return fortune
    if post_object.has_key('id_str') and screen_name != None:
      return api.updateStatus(status=fortune, in_reply_to_status_id=post_object['id_str'])
    else:
      return api.updateStatus(status=fortune)

  def chooseFortune(self, max_len=140, screen_name=None):
    fortune = ''
    if screen_name != None:
      fortune += '@' + screen_name + ' '
      max_len -= len(fortune)
    tmp_fortune = random.choice(self.fortunes)
    count = 0
    while len(tmp_fortune) > max_len:
      if count > 1000:
        return None
      tmp_fortune = random.choice(self.fortunes)
      count += 1
    fortune += tmp_fortune
    return fortune
