def applyheart(Func):
    def wrapper():
        print("❤️ " * 20)  # Red heart emoji
        Func()
        print("❤️ " * 20)  # Red heart emoji
    return wrapper

def applystar(func):
    def wrapper():
        print("⭐ " * 20)  # Star emoji
        func()
        print("⭐ " * 20)
    return wrapper

def applyemoji(func):
    def wrapper():
        print("😊"*20)
        func()
        print("😊"*20)
    return wrapper

@applyheart
@applystar
@applyemoji
def say_Abdullah():
    print("Abdullah Athar")

say_Abdullah()