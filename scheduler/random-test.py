from scheduler.random_scheduler import RandomScheduler

def test1():
    mp = {'a':[1,2,3], 'b':[1,4], 'c':[5], 'd':[3,1]}
    print RandomScheduler(None, 'abcd', mp).schedule()

test1()
