
At some point in a career in data science, software development or data engineering you will be looking to develop a piece of code that runs alongside another piece of code. For example, you might want to:

* Use all of your processors when running a script
* Consume social media data as it is created
* Create a super simple task scheduler without an ugly while True loop
* Understand how Jupyter notebooks work
* Write to a database and move on to the next task without waiting for confirmation
* Call a function and throw an exception if it takes too long

There are numerous ways of achieving such concurrency. If creating a project to run on one or a few machines which needs good exception handling then I find tools like Twisted, Tornado and Dask/Distributed ideal for the above tasks.

First a little bit of theory:

What are the different ways that code can run?

Let's try an analogy... 
 
Let's say I am frying eggs and making toast for all the family.

Let's break down the tasks... 
 
Toast bread
Butter toast
Heat up frying pan
Add oil
Break eggs into pan
Wait until the right moment
Flip the eggs carefully for a few seconds
Put on more toast
Make sure everyone is at the table
Server the eggs on toast

## What are the possible ways we could do these tasks?

### 1) Procedural

Let's say my toaster is one of these:

![](https://www.picclickimg.com/00/s/MTA2NlgxNjAw/z/RGEAAOSwNSxVXQQw/$/Antique-Westinghouse-Flip-Up-Chrome-Toaster-WORKS-ORIG-CORD-_1.jpg)

And my kitchen is really badly laid out - in fact there are no sockets in my kitchen and so the toaster is in the dining room.

How am I going to get everyone's toast cooked as well as their eggs?

One way to avoid burning anything would be:

Half cook toast on each side then leave in the toaster to keep warm.

Cook eggs

Finish cooking toast

Combine and serve

### 2) Multi process

Another way of getting round these constraints is just to ask for help. In this case two of us can get everything done in a coordinated way but it relys on two people being happy to cook the breakfast.

### 3) Multi threaded

In this case I have my toaster next to my frying pan and I can keep my hands and eyes on both at once. In this way I get everything cooked and I can slow down or speed up the eggs to make sure the eggs and the toast are all just right. I use my multiple arms to acheive this.

### 4) Asynchronous Coroutines

In this case I decide to throw away my old toaster and get a new one which pops up and also detects when the bread is just right. 

[http://news.bbc.co.uk/1/hi/england/cambridgeshire/4291816.stm]

I also get myself the amazing "Heston Blumenthal BEG800SIL One Degree Precision Poacher"

[https://www.go-electrical.co.uk/sage-heston-blumenthal-beg800sil-the-one-degree-precision-poacher.html?gclid=CJqwia-nk9MCFY8Q0wodLqcL4Q]

Now I can simply set off my toast and eggs at the appropriate time and also have time to do some other things, perhaps get out my autonymous vacuum cleaner and send it to trip someone up.

Note that throughout the coroutine example the breakfast preparer (me) is only ever doing one thing at a time. I can set off a bunch of background tasks and then relax and wait for them to tell me they are done. Arguably method 4 is the least stressful, the technology has handed back control to me. If however the technology has not been implemented well then everything could go wrong.

So what is the programatic equivalent of turning on the toaster then leaving it and waiting for the sound of it popping up?

1. Send task to be run which requires no processing on my machine
2. Get back an acknowledgement and wait for task completion (we wait using a Future object)
3. Do some other stuff in the meantime
4. Hear an event and go back to the task to do whatever needs finishing off.




# Example 1: Sleep for 8 hours in 10 seconds:

One of the first things to understand about async programming is the execution model. We are used to a python script simply following the lines of code, async is different and therefore I can "sleep" without the CPU waiting.

    import asyncio
    import time
    
    t = time.time()
    
    @asyncio.coroutine
    def bar():
    
        yield from asyncio.sleep(8)   # Note that the sleep function myust be asyncronous"

    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(bar()) for i in range(0,3600)]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()
    
    print(time.time()-t)
    
    

python 2
    
    
# Example 1: Written the 'new' way
    

    import asyncio
    import time
    
    t = time.time()
    
    
    async def  bar():
    
        await asyncio.sleep(8)
    
    
    
    
    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(bar()) for i in range(0,3600)]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()
    
    print(time.time()-t)


What are the key features of the above functions?


* The function we execute is an asynchronous coroutine
* It is wrapped in a "Task" which is a type of "Future" - this is a placeholder for the result of the function
* The sleep function is also an asynchronous coroutine (time.sleep() would not work here)
* The tasks are submitted to an event loop
* `yield from` or `await` are used to send back control to the event loop so it can do other things.

These feautures will crop up again when we use other asynchronous libraries

#Excersise 1: 

Implement the above function in tornado and python 3


Now, let's make it run on python 2



The interesting feature of the python 2 implmentation is that we can only break the flow control of the application by using an exception. Various new language features have been added in python 3 which give us more options.


#We keep using asyncios `event_loop` and Tornado's `IOLoop`... What is an event loop???

"In computer science, the event loop, message dispatcher, message loop, message pump, or run loop is a programming construct that waits for and dispatches events or messages in a program."

Events were introduced in Python 3 as we have seen, Python 2 does not have anything that can break the flow of a program apart from exceptions. 

If we first consider a loop that is waiting for only one kind of event, that is simpler to conceptualise... 
 
 From the following URL I can open a connection and then follow every change to Wikipedia.
 
https://stream.wikimedia.org/v2/stream/recentchange

We can read data synchonously from the URL like this:

    import requests
    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    import json
    r = requests.get(url, stream=True)
    for line in r.iter_lines(decode_unicode=True):
        if line:
            if line.startswith("data:"):
                datapoint = line[5:]
                data = json.loads(datapoint)
                print(data)

     
Question... Is this compatible with a Tornado/ Asyncio event loop? Can we use it to send events and have them processed?

Answer - no! The generator response.iter_lines is blocking. Therefore we need to read the http request in a nonblocking way OR use another process/thread.


Non-blocking read


    from tornado import ioloop, gen, httpclient
    
    @gen.coroutine
    def main():
        http_client = httpclient.AsyncHTTPClient()
    
        def streaming_callback(data):
            print(data)
    
        yield http_client.fetch('https://stream.wikimedia.org/v2/stream/recentchange', streaming_callback=streaming_callback, request_timeout=3600)
    
    
    if __name__ == '__main__':
        ioloop.IOLoop.instance().run_sync(main)


OK, so that works but now we are recieving packets that may be partial data points, therefore we need to store state between packets and collect them up.

    from tornado import ioloop, gen, httpclient
    import json
    
    class DataReciever(object):
        def __init__(self):
            self.partial_data = None
    
    
        def streaming_callback(self, input):
            data = input.decode("utf-8")
            lines = data.splitlines()
            for line in lines:
                if self.partial_data is not None:
                    line = self.partial_data + line
                    self.partial_data = None
                if len(line) > 0  and len(line) < 100 and "data:".startswith(line[:4]):
                    self.partial_data = line
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:])
                        print(data)
                    except (ValueError, IndexError):
                        self.partial_data = line
    
    
    @gen.coroutine
    def main():
        http_client = httpclient.AsyncHTTPClient()
        dr = DataReciever()
        yield http_client.fetch(
            'https://stream.wikimedia.org/v2/stream/recentchange',
            streaming_callback=dr.streaming_callback,
            request_timeout=3600
        )
    
    
    if __name__ == '__main__':
        ioloop.IOLoop.instance().run_sync(main)

Great! so now we are receiving JSON data in a tornado coroutine, 

How do we save these in a database?

    from tornado import ioloop, gen, httpclient
    import json
    import motor
    
    class DataReciever(object):
        def __init__(self):
            self.partial_data = None
            self.client = motor.motor_tornado.MotorClient()
            self.db = self.client['test_database']
    
        # def data_from_line(self, line):
        def my_callback(self, result, error):
            print('result %s' % repr(result.inserted_id))
    
        def streaming_callback(self, input):
            data = input.decode("utf-8")
            lines = data.splitlines()
            for line in lines:
                if self.partial_data is not None:
                    line = self.partial_data + line
                    self.partial_data = None
                if len(line) > 0  and len(line) < 100 and "data:".startswith(line[:4]):
                    self.partial_data = line
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:])
                        self.db.test_collection.insert_one(data, callback=self.my_callback)
                    except (ValueError, IndexError):
                        self.partial_data = line
    
    
    @gen.coroutine
    def main():
        http_client = httpclient.AsyncHTTPClient()
        dr = DataReciever()
        yield http_client.fetch(
            'https://stream.wikimedia.org/v2/stream/recentchange',
            streaming_callback=dr.streaming_callback,
            request_timeout=3600
        )
    
    
    if __name__ == '__main__':
        ioloop.IOLoop.instance().run_sync(main)
            
            
This is all very well but more complex than the requests example.
           
There are also two callbacks! We were supposed to be writing cleaner code which avoids callbacks. We are also having to handle the raw http data.

Additionally, it is harder to debug errors as they will not have a full stack trace, for example:

    from tornado import ioloop, gen, httpclient
    import json
    import motor
    
    class DataReciever(object):
        def __init__(self):
            self.partial_data = None
            self.client = motor.motor_tornado.MotorClient()
            self.db = self.client['test_database']
    
        # def data_from_line(self, line):
        def my_callback(self, result, error):
            print('result %s' % repr(result.inserted_id))
    
        def streaming_callback(self, input):
            data = input.decode("ascii")
            lines = data.splitlines()
            for line in lines:
                if self.partial_data is not None:
                    line = self.partial_data + line
                    self.partial_data = None
                if len(line) > 0  and len(line) < 100 and "data:".startswith(line[:4]):
                    self.partial_data = line
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:])
                        self.db.test_collection.insert_one(data, callback=self.my_callback)
                    except (ValueError, IndexError):
                        self.partial_data = line
    
    
    @gen.coroutine
    def main():
        http_client = httpclient.AsyncHTTPClient()
        dr = DataReciever()
        yield http_client.fetch(
            'https://stream.wikimedia.org/v2/stream/recentchange',
            streaming_callback=dr.streaming_callback,
            request_timeout=3600
        )
    
    
    if __name__ == '__main__':
        ioloop.IOLoop.instance().run_sync(main)
            
Enter aiohttp...

Asyncio has an http library, we need to install it with pip and the docs are not as good as Tornado but we can make use of some interesting new language features..

    
    import asyncio
    import aiohttp
    ioloop = asyncio.get_event_loop()
    async def getdata():
         async with aiohttp.ClientSession() as session:
             async with session.get('https://stream.wikimedia.org/v2/stream/recentchange') as resp:
                 async for line in resp.content:
                     print(line)
    ioloop.run_until_complete(getdata())


Task: Use the tornado asyncio bridge (see http://www.tornadoweb.org/en/stable/asyncio.html#tornado.platform.asyncio.AsyncIOMainLoop) to write the data to MongoDB using motor.

######NEEDS ANSWER!!!




### Scheduling repeated tasks

We have learned that:

* Asyncio and Tornado work well for external HTTP requests and other things where an event is waited for
* A wrapper Task class is used to wrap the result of a function in a future
* Where synchronous code needs to be run, a ProcessPoolExecutor can be used

Task: Take this terminal clock example and reimplement it using asyncio or tornado to provide the timer

    import time
    
    def overprint(stringdata):
        print(stringdata , end="\r")
        
        
    def get_time():
        return time.strftime("%d-%m-%Y %H:%M:%S")
    
    
    while True:
        start = time.time()
        overprint(get_time())
        sleep_for = 1 - (start - time.time())
        time.sleep(sleep_for)
        



#Running a task and timing out if it takes too long

This seemingly simple question is in fact pretty difficult in python. HTTP libraries like aiohttp, and tornado implement timeout functions, but to actually timeout a piece of blocking code there are further difficulties...

The first port of call is to try to wrap a process in a future and then cancel the future. This fails to work correctly as the future cancels and the task is left running.

    import asyncio
    import time
    from concurrent.futures import ProcessPoolExecutor
    
    def block_then_print():
        time.sleep(10)
        print("done")
    
    @asyncio.coroutine
    def coro(loop, ex):
        
        yield from loop.run_in_executor(ex, block_then_print)  # This can be interrupted.
    
    ex = ProcessPoolExecutor(2)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(coro(loop, ex), 1))
    
Using raw processes it is possible to timeout a task by by using signals as demonstrated by this decorator:

    import time
    import timeout_decorator
    
    @timeout_decorator.timeout(5)
    def mytest():
        print ("Start")
        for i in range(1,10):
            time.sleep(1)
            print ("%d seconds have passed" % i)
    
    if __name__ == '__main__':
        mytest()

Equally we can also add a timeout when we shell out to a subprocess using `subprocess.run` new in python 3.5.

from subprocess import STDOUT, check_output, TimeoutExpired
try:
    output = check_output(["ping", "google.com"], stderr=STDOUT, timeout=2)
except TimeoutExpired as e:
    print(e.output.decode("utf-8"))


This would work fine for small scripts but use of signals, shelling out and raw processes are not reccomended in larger projects due to:

* Platform differences
* Possibility of zombie processes
* Lack of control over how many processes are open


So how should we proceed???

A few of the python task fromeworks suggest that they support task cancellation but upon closer inspection `Celery` and `Dask/Distributed` only support cancellation before execution starts not during execution.

Often people may want to check if the task needs cancelling during execution, dask/distributed will check between subtasks but a timeout means killing the task dead!

Luigi to the rescue!

Luigi also uses some tornado and event loops for communication but also helps keep track of subprocesses within workers. This gives all the flexibility of the subprocess example above along with the stability of a proper data processing framework.

    import luigi
    from time import sleep
    class MyTask(luigi.Task):
        worker_timeout = 5
        def run(self):
            sleep(10)
            return luigi.LocalTarget("result", "done")    
    
The task can be run like this:

    PTHYONPATH=$(pwd) luigi --module luigi_timeout MyTask --local-scheduler --workers=


# Futures can be used to wait for completion from an external process

So far we have learned a little about how to call asynchronous functions and run background tasks. Each of the tasks we have done has had an input and an output without lots of intermediate steps. This is useful to understand the principles of async python but it is now time to join some things together into a data processing pipeline.

Passing futures as the argument for the next function can allow CPU time to be saved. Complex concurrent workflows can be made to look simple and procedural because futures can be passed around before they are "done". 

For example: if the task is to download a list of images and then resize them, the resize operations can start whenever an individual piece of data is ready.

Further requirements for a data science tool might be that it can handle exceptions gracefully and allow other tasks to be run even after an exception has been thrown. We amy also want to be able to scale seamlessly from laptop to a cluster.

Futures come in a few flavours... 

In this tutorial we have worked with tornado futures and asyncio futures. You may also come across concurrent.futures, These are another part of the standard library and are used when wrapping synchronous cpu-bound tasks.

When seeing all of these options it can become a little overwhelming. Therefore the pattern I will teach in this tutorial is the one I believe is the most scalable and flexible. That is to use the Dask/Distributed framework.

Dask/Distributed wraps tornado and concurrent.futures to provide a cluster server and a set of patterns for getting the most out of these tools. Because there is a fully featured cluster server, it is easier to scale up your code to run on multiple machines.

It is built out of the building blocks we have discussed:

* Tornado IOLoops for communication and async tasks
* ThreadPoolExecutor per worker for running synchronous code
* Additional protocol available for networking - 0mq

#Example: Download a list of image URLs, resize the images and write them to disk


Wait for file
download with coroutine on client
run tasks on the callback using the client


#Task 






























https://www.blog.pythonlibrary.org/2016/07/26/python-3-an-intro-to-asyncio/

What types of task does this apply to?

Whenever we connect  to another computer or service over network there is a potential to make savings provided that:

* A coroutine exists to make the outbound call
* The remote service is able to acknowledge without first processing and send back a message when complete

A very small % of existing code fulfils this criteria.

This means that we need to do some work in order to find out if the task is done. This is still doable but the coroutine needs to be run in a "Task", thread or process.

Therefore our workflow becomes:

Create a thread or process and send a task to be run->
    Get back an acknowledgement and wait for task completion (we wait using a Future object)
    Do some other stuff
    Task/ Thread finishes and returns its result to the future
    Hear an event and go back to the task result to do whatever needs finishing off.

How do we "hear" the event???

This detail is not necessarily important - a good answer is "we use the right framework in the right way". So let's see how this stuff works:









# Example 3: Resize a set of images in memory

# Example 4: Download a spreadsheet of urls then download the images and resize them

# Example 5: Aggregate Tweets with Twisted e.g. 10 second sampling of tweets

# Example 6: Avoid overloading a server when crawling data


















When we think about programming there are some other tasks which don't require the computer to 'think' but do take time. Event driven programming was invented to take advantage of these situations by starting up more tasks by running more things at a time than would be possible were the computer having to think.


Event loop - you can think of this as a while True loop which looks for signals to tell it when to run something

Coroutine - a special python function which has been made to run in an async framework

Future - a reference to a function which has been scheduled to be run and which will eventually contain the result of the function or an exception

