from twilio.rest import Client

#account_sid=AC72e31f327b536b9febfbe760785772d4
#account_auth=60778dfe370f082e18f1ff02667dcba9
class Sms():
	def __init__(self, account_sid="AC72e31f327b536b9febfbe760785772d4", account_auth="60778dfe370f082e18f1ff02667dcba9", send_num="+13128542414"):
		self.client = Client(account_sid,account_auth)
		self.send_num = send_num

	def send_msg(self,resv_num,msg):
		self.client.messages.create(to=resv_num,from_=self.send_num,body=msg)
