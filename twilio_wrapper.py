
class Twilio:
    def __init__(self, Client):
        self.twilio_client = Client

    def send_sms(self,from_number, to_number, message):

        message = self.twilio_client.messages.create(
            from_=from_number,
            to=to_number,
            body=message
        )
        return message
    
