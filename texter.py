import twillio_keys
import string

from twilio.rest import TwilioRestClient 
client = TwilioRestClient(twillio_keys.ACCOUNT_SID, twillio_keys.AUTH_TOKEN) 

def num_parse(s):
    return "".join([c for c in s if c in string.digits])[-10:]
def send_message(num, message):
    client.messages.create( 
    	from_="+1"+num_parse("4084776092"),
    	to_="+1"+num_parse(num), 
    	body=str(message)
    )