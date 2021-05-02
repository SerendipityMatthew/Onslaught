import logging


def execute_cmd(func):
    def wrapper():
        logging.debug("%s is running" % func.__name__)
        return func()  # 把 foo 当做参数传递进来时，执行func()就相当于执行foo()

    return wrapper


def foo():
    print('i am foo')


fooHello = execute_cmd(foo)  # 因为装饰器 use_logging(foo) 返回的时函数对象 wrapper，这条语句相当于  foo = wrapper
fooHello()
