def hello(message):
    print(f"Hello {message}")

def callb(f,a):
    f(a)


callb(hello, "fpp")
callb(hello, "xx")

