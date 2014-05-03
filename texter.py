import twillio_keys
import string

from twilio.rest import TwilioRestClient 
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 

def num_parse(s):
    return "".join([c for c in s if c in string.digits])[-10:]
def send_message(num, message):
    client.messages.create( 
    	from_="+1"+num_parse(num), 
    	body=str(message),  
    )