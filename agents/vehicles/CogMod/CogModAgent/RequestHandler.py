class RequestHandler():
    def __init__(self, subtasks_queue, servers_dict):
        self.subtasks_queue = subtasks_queue
        self.servers_dict = servers_dict

        # print('server dict ', self.servers_dict)

        
        pass

    # each server implements a process_request method
    # the method process one request from the existing 
    # request queue of the server
    def process_request_in_cognitive_servers(self):
        for server in self.servers_dict.values():
            server.process_request()
        pass

    # get responses from all the servers 
    # server process request and put the processed 
    # response in the buffers

    def get_responses_from_buffers(self):
        response_queue = []
        for server in self.servers_dict.values():
            response = server.get_response()
            if response:
                response_queue = response_queue + response
        return response_queue

    # first create the subtasks response dictionary for the available subtasks
    # in the subtasks_queue. populate the dictionary with the responses from the
    # buffers. at the end ontick method of the subtasks will be called with the
    # collected responses in the dictionary
    # subtasks create requests during ontick
    #  we collect the request with get_request_from_subtasks method

    def send_response_and_localmap_to_subtasks(self, responses, localMap):
        
        subtask_responses = {}

        for subtask in self.subtasks_queue:
            subtask_responses[subtask.subtask_type] = []

        for response in responses:
            subtask_responses[response.receiver].append(response)
        
        for subtask in self.subtasks_queue:
            subtask.onTick(subtask_responses[subtask.subtask_type], localMap)
            
    
    def get_request_from_subtasks(self):
        request_queue = []
        for subtask in self.subtasks_queue:
            request_queue = request_queue + subtask.get_request()
        return request_queue

    def send_request_to_servers(self, subtask_requests):
        for request in subtask_requests:
            self.servers_dict[request.receiver].add_request(request)
        pass
        