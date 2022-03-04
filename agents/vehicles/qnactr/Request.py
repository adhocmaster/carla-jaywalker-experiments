

class Request():
    def __init__(self, sender, receiver, data: dict):
        self.sender = sender
        self.receiver = receiver
        self.data = data
        pass

    def __str__(self):
        return "\nsender: " + str(self.sender) + " requested: " + str(self.data.keys())  + " receiver: " + str(self.receiver) 

    # after processing a request the processed data is sent back to the 
    # sender by modifying the request (swapping sender and receiver, change request type)
    def after_process(self, processed_data):
        self.data = {}
        self.data = processed_data
        self.swap_sender_receiver()
        pass

    def swap_sender_receiver(self):
        self.sender, self.receiver = self.receiver, self.sender
        pass