
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
 
Let's say I am frying egs and making toast for all the family.

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

OK so we know what we are going to do, but what order shall we go about things?

1) Procedural

Let's say my toaster is one of these:

[https://www.picclickimg.com/00/s/MTA2NlgxNjAw/z/RGEAAOSwNSxVXQQw/$/Antique-Westinghouse-Flip-Up-Chrome-Toaster-WORKS-ORIG-CORD-_1.jpg] 

And my kitchen is really badly laid out - in fact there are no sockets in my kitchen and so the toaster is in the dining room.

How am I going to get everyone's toast cooked as well as their eggs?

One way to avoid burning anything would be:

Half cook toast on each side then leave in the toaster to keep warm.

Cook eggs

Finish cooking toast

Combine and serve

2) Multi process

Another way of getting round these constraints is just to ask for help. In this case two of us can get everything done in a coordinated way but it relys on two people being happy to cook the breakfast.

3) Multi threaded

In this case I have my toaster next to my frying pan and I can keep my hands and eyes on both at once. In this way I get everything cooked and I can slow down or speed up the egs to make sure the eggs and the toast are all just right.

4) Coroutines

In this case I decide to throw away my old toaster and get a new one which pops up . Now I can concentrate on my eggs most of the time and life is plenty easier. When the eggs are done I can go back to the toaster knowing that the toast will be siting there still warm for me.

Note that throughout the coroutine example the breakfast preparer (me) is only ever doing one thing at a time. I can set off a backbround task (the toasting) which takes some time to set up but then I am only thinking about the egg. Arguably method 4 is the least stressful. 

So what is the programatic equivalent of turning on the toaster then leaving it and waiting for the sound of it popping up?

What we are doing... 

Send task to be run ->
    Get back an acknowledgement and wait for task completion (we wait using a Future object)
    Do some other stuff
    Hear an event and go back to the task to do whatever needs finishing off.

# Example 1: Sleep for 8 hours in 10 seconds:

    import asyncio
    import time
    
    t = time.time()
    
    @asyncio.coroutine
    def bar():
    
        yield from asyncio.sleep(8)
    
    
    
    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(bar()) for i in range(0,3600)]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()
    
    print(time.time()-t)
    
    
    
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


# Example 2: Make 100 simultaneous http requests


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

Why would we want to do this? Why not just use standard threads?

Complex concurrent workflows can be made to look simple and procedural because futures can be passed around before they are "done". 

# Example 3: Resize a set of images in memory

# Example 4: Download a spreadsheet of urls then download the images and resize them

# Example 5: Aggregate Tweets with Twisted e.g. 10 second sampling of tweets

# Example 6: Avoid overloading a server when crawling data


















When we think about programming there are some other tasks which don't require the computer to 'think' but do take time. Event driven programming was invented to take advantage of these situations by starting up more tasks by running more things at a time than would be possible were the computer having to think.


Event loop - you can think of this as a while True loop which looks for signals to tell it when to run something

Coroutine - a special python function which has been made to run in an async framework

Future - a reference to a function which has been scheduled to be run and which will eventually contain the result of the function or an exception

