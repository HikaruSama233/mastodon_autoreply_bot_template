from mastodon import Mastodon
import datetime
import os
import html2text
import time


class Bot:
    def __init__(self, client_id, access_token):
        """Intiate a Mastodon bot.

        :param client_id: (str) path to clientcred.secret file.
        :param access_token: (str) path to usercred.secret file.
        """
        self._client = client_id
        self._token = access_token
        self._handle = ""
        self._atname = ""
        self._mentions_queue = []
        self._text_extractor = html2text.HTML2Text()
        self._text_extractor.ignore_links = True

    def _check_notifications(self):
        notifications = self._bot.notifications(mentions_only=True)
        current_time = datetime.datetime.now()
        if len(notifications) > 0:
            print("{} Total notifications {}".format(current_time, len(notifications)))
            self._mentions_queue = notifications
            while len(self._mentions_queue) > 0:
                self._read_mention(self._mentions_queue[0])
        elif str(current_time.minute) == '0':
            print("{} No notifications".format(current_time))

    def _read_mention(self, obj):
        notification_id = obj['id']
        status = obj["status"]
        account = status['account']
        mentions = status['mentions']
        reply = "Can you hear me? "
        ending = "Absolutely! "
        # this bot does not reply to another bot.
        if account['bot']:
            self._bot.notifications_dismiss(notification_id)
            self._mentions_queue.pop(0)
            return
        # clean html decorations
        # if the bot is mentioned, remove the mention text from status content
        # before responding
        content_text = self._text_extractor.handle(status['content']).replace(self._atname, "").strip()
        # check somebody only @you or @many_accounts
        if len(mentions) == 1:
            # do something based on content_text
            reply = self._call_someone(content_text)
        else:
            # do something else or do nothing
            pass
        try:
            self._respond(status, reply + ending)
        except Exception as e:
            print(e)
        # mark it as read
        try:
            self._bot.notifications_dismiss(notification_id)
        except Exception as e:
            print(e)
        self._mentions_queue.pop(0)

    def _call_someone(self, text):
        # You can only change this function
        reply = "blahblah"
        return reply

    def _respond(self, status, content):
        """Reply to a status with content

        :param status: (dict) the status to respond to.
        :param content: When ``content`` is a string.
        """
        if not content:
            raise ValueError(f"Response to {status['id']} empty; aborted")
        elif type(content) == str:
            args = {
                "to_status": status,
                "status": content,
            }
        else:
            pass
        self._bot.status_reply(in_reply_to_id=status['id'], **args)


    def run(self):
        # Remember to change api_base_url
        self._bot = Mastodon(client_id=self._client, access_token=self._token, api_base_url="URL for your Mastodon instance of choice")
        print("Connecting to fediuniverse...")
        me = self._bot.account_verify_credentials()
        # Remeber to change the username without @ sign
        if me['acct'] == 'Your user name':
            print("Successfully connected!")
        self._handle = me['acct']
        self._atname = "@" + me["username"]
        while 1:
            # Check every 3 seconds. Do not check too often!
            time.sleep(3)

            if len(self._mentions_queue) == 0:
                self._check_notifications()


if __name__ == "__main__":
    bot = Bot(client_id='clientcred.secret', access_token='usercred.secret')
    bot.run()
