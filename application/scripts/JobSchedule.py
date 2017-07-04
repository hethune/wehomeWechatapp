from multiprocessing import cpu_count,Process,Queue
import threading
import os

class JobSchedule(object):
  def __init__(self, function,queue,prcesscount=None,thread_count=1):
    self.function = function
    self.queue = queue
    self.thread_count = thread_count
    self.prcesscount = [prcesscount,cpu_count()][prcesscount is None]

  def _makethread(self,target,thread_count,args):
    thread_pool  = []
    for x in xrange(thread_count):
      t = threading.Thread(target=target,args=(args,))
      thread_pool.append(t)
    for process in thread_pool:
      process.start()
    for process in thread_pool:
      process.join()  

  def start(self):
    process_pool  = []
    for x in xrange(self.prcesscount):
      p = Process(target=self._makethread,args=(self.function,self.thread_count,self.queue))
      process_pool.append(p)
    for process in process_pool:
      process.start()
    for process in process_pool:
      process.join()  