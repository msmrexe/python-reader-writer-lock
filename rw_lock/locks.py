# rw_lock/locks.py

"""
Contains three implementations of the Reader-Writer Lock:
1. ReaderPriorityRWLock: Can starve writers.
2. WriterPriorityRWLock: Can starve readers.
3. FairRWLock: FIFO (first-come, first-served) implementation.
"""

import threading
from contextlib import contextmanager

# -----------------------------------------------------------------
# 1. Reader-Priority Implementation
# -----------------------------------------------------------------
class ReaderPriorityRWLock:
    """
    A Reader-Writer Lock that gives priority to readers.
    A writer can only acquire the lock if there are no active
    or waiting readers.
    
    This implementation can lead to WRITER STARVATION.
    """
    
    def __init__(self):
        self._monitor = threading.Lock()
        
        self._reader_count = 0
        
        # Condition for writers to wait on
        self._writer_ok = threading.Condition(self._monitor)
        # Lock to ensure only one writer can check
        self._writer_lock = threading.Lock()

    def _read_acquire(self):
        with self._monitor:
            self._reader_count += 1
            # If this is the first reader, it "acquires" the lock
            # on behalf of all readers
            if self._reader_count == 1:
                self._writer_lock.acquire() # Block writers

    def _read_release(self):
        with self._monitor:
            self._reader_count -= 1
            # If this is the last reader, it "releases" the lock
            if self._reader_count == 0:
                self._writer_lock.release() # Allow writers

    def _write_acquire(self):
        # A writer must be the *only* thread to acquire this
        self._writer_lock.acquire()

    def _write_release(self):
        self._writer_lock.release()

    @contextmanager
    def read(self):
        self._read_acquire()
        try:
            yield
        finally:
            self._read_release()

    @contextmanager
    def write(self):
        self._write_acquire()
        try:
            yield
        finally:
            self._write_release()


# -----------------------------------------------------------------
# 2. Writer-Priority Implementation (Your original, refined)
# -----------------------------------------------------------------
class WriterPriorityRWLock:
    """
    A Reader-Writer Lock that gives priority to waiting writers.
    
    This implementation can lead to READER STARVATION.
    """

    def __init__(self):
        self._monitor = threading.Lock()
        self._readers_ok = threading.Condition(self._monitor)
        self._writers_ok = threading.Condition(self._monitor)
        
        self._reader_count = 0
        self._writer_active = False
        self._writer_waiting_count = 0

    def _read_acquire(self):
        with self._monitor:
            # Readers must wait if a writer is active or waiting.
            while self._writer_active or self._writer_waiting_count > 0:
                self._readers_ok.wait()
            self._reader_count += 1

    def _read_release(self):
        with self._monitor:
            self._reader_count -= 1
            # If last reader out, notify a waiting writer
            if self._reader_count == 0 and self._writer_waiting_count > 0:
                self._writers_ok.notify()

    def _write_acquire(self):
        with self._monitor:
            self._writer_waiting_count += 1
            # A writer must wait if readers are active or another writer is active
            while self._reader_count > 0 or self._writer_active:
                self._writers_ok.wait()
            self._writer_waiting_count -= 1
            self._writer_active = True

    def _write_release(self):
        with self._monitor:
            self._writer_active = False
            # Give priority to other waiting writers
            if self._writer_waiting_count > 0:
                self._writers_ok.notify()
            else:
                # No writers waiting, wake up all waiting readers
                self._readers_ok.notify_all()

    @contextmanager
    def read(self):
        self._read_acquire()
        try:
            yield
        finally:
            self._read_release()

    @contextmanager
    def write(self):
        self._write_acquire()
        try:
            yield
        finally:
            self._write_release()


# -----------------------------------------------------------------
# 3. Fair (FIFO) Implementation
# -----------------------------------------------------------------
class FairRWLock:
    """
    A "Fair" Reader-Writer Lock.
    
    Grants access in FIFO (first-come, first-served) order.
    Uses a single queue condition to wake up all threads,
    which then re-check their conditions.
    
    This implementation should prevent starvation for both.
    """

    def __init__(self):
        self._monitor = threading.Lock()
        
        self._readers_active = 0
        self._writer_active = False
        
        # Threads wait on this condition in FIFO order
        self._queue = threading.Condition(self._monitor)
        
        # Count of *all* waiting threads (readers or writers)
        self._waiting_count = 0

    def _read_acquire(self):
        with self._monitor:
            self._waiting_count += 1
            # Readers must wait if a writer is active
            while self._writer_active:
                self._queue.wait()
            self._waiting_count -= 1
            self._readers_active += 1

    def _read_release(self):
        with self._monitor:
            self._readers_active -= 1
            # If this is the last reader and threads are waiting,
            # wake them all up so the one at the front
            # (which could be a writer or more readers) can go.
            if self._readers_active == 0 and self._waiting_count > 0:
                self._queue.notify_all()

    def _write_acquire(self):
        with self._monitor:
            self._waiting_count += 1
            # A writer must wait if any readers are active
            # OR if another writer is active
            while self._readers_active > 0 or self._writer_active:
                self._queue.wait()
            self._waiting_count -= 1
            self._writer_active = True

    def _write_release(self):
        with self._monitor:
            self._writer_active = False
            # Wake up all waiting threads. The 'while' loops
            # will ensure only the correct ones proceed (either
            # one writer or a group of readers).
            if self._waiting_count > 0:
                self._queue.notify_all()

    @contextmanager
    def read(self):
        self._read_acquire()
        try:
            yield
        finally:
            self._read_release()

    @contextmanager
    def write(self):
        self._write_acquire()
        try:
            yield
        finally:
            self._write_release()
