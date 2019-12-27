import pickle


class Test:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def p(self):
        print(f"{self.x}: {self.y}")


a = Test(5, 7)
pickled = pickle.dumps(a)
b = pickle.loads(pickled)
print(b.x)
b.p()
