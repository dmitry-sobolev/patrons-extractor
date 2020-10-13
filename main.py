# Only dependency needed
import threading
import time

from patrons import get_patrons
from sheets import write_patrons


def periodic_task(interval, times=-1):
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            stop = threading.Event()

            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    function(*args, **kwargs)
                    i += 1
                    stop.wait(interval)

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return t
        return wrap
    return outer_wrap


@periodic_task(86400)
def my_periodic_task():
    # This function is executed every 10 seconds
    patrons = get_patrons()
    print("Patrons: ", patrons)

    write_patrons(patrons)


def run():
    t = my_periodic_task()
    while t.is_alive():
        time.sleep(1)


if __name__ == '__main__':
    run()
