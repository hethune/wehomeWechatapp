from multiprocessing import cpu_count, Process, Queue, Manager
import threading
import os
from Queue import Empty
from threading import Lock as TL
from multiprocessing import Lock as PL
from multiprocessing import Pool
import time
from tqdm import tqdm

TL = TL()
PL = PL()
con = threading.Condition()

class JobSchedule(object):
  def __init__(self, function,queue,prcesscount=None,thread_count=1, max_size=0):
    self.function = function
    self.queue = queue
    self.message_queue = Queue()
    self.thread_count = thread_count
    self.max_size = max_size
    # self.share = Manager().dict()
    # self.share['pbar'] = pbar
    # self.pbar = pbar
    self.prcesscount = [prcesscount,cpu_count()][prcesscount is None]

  def _makethread(self,target,thread_count,args):
    thread_pool  = []
    for x in xrange(thread_count):
      t = threading.Thread(target=target,args=(self.update_pbar, args))
      thread_pool.append(t)
    for process in thread_pool:
      process.start()
    for process in thread_pool:
      process.join()  

  def start(self):
    # pbar thread
    pbar_thread = threading.Thread(target=self.make_pbar_thread)
    pbar_thread.start()

    process_pool  = []
    for x in xrange(self.prcesscount):
      p = Process(target=self._makethread,args=(self.function,self.thread_count,self.queue))
      process_pool.append(p)
    for process in process_pool:
      process.start()
    for process in process_pool:
      process.join()

    self.update_pbar('finish')

  def make_pbar_thread(self):
    pbar = tqdm(total=self.max_size)
    while True:
      message = self.message_queue.get()
      if message == 'progress':
        pbar.update()
      if message == 'finish':
        return

    # PL.acquire()
    # TL.acquire()
    # self.share['pbar'] += 1
    # print self.share['pbar']
    # self.share['pbar'].update()
    # TL.release()
    # import time
    # time.sleep(1)
    # PL.release()
    # while True:
    # try:
    # except Empty:
    #   return

  def update_pbar(self, message):
    self.message_queue.put(message)