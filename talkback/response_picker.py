import random

class ResponsePicker(object) :

    # initialize ResponsePicker class
    def __init__(self) :
        self.responses = ['test1',
                          'test2',
                          'test3',
                          'test4']

    # return a random response
    def pick(self) :
        return random.choice(self.responses)
