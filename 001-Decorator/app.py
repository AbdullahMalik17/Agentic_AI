# Basic decorator syntax
def my_decorator(func):
    def wrapper():
        print("Something happens before the function is called")
        func()
        print("Something happens after the function is called")
    return wrapper

# Using the decorator
@my_decorator        # @ is used to apply the decorator
def say_hello():
    print("Hello!")
say_hello()    
