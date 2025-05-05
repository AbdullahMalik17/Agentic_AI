def say_greeting(func):
    def wrapper():
        print("Assalam o Alaikum ")
        func()
        print("Good Bye!")
    return wrapper 

@say_greeting
def say_abdullah():
    print("Abdullah!")     

say_abdullah()      