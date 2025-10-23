# rw_lock/lock.py

"""
Contains a self-contained, Writer-Priority Reader-Writer Lock.
"""

import threading
from contextlib import contextmanager

class WriterPriorityRWLock:
    """
    A Reader-Writer Lock that gives priority to waiting writers.
    
    This implementation prevents reader starvation by blocking
    new readers if a writer is waiting.
    """

    def __init__(self):
        self._monitor = threading.Lock()
        
        # Condition for readers to wait on
        self._readers_ok = threading.Condition(self._monitor)
        # Condition for writers to wait on
        self._writers_ok = threading.Condition(self._monitor)
        
        # --- Internal State ---
        self._reader_count = 0
        self._writer_active = False
        self._writer_waiting_count = 0

    def _read_acquire(self):
        """Acquires the lock for reading."""
        with self._monitor:
            # Readers must wait if a writer is active
            # OR if a writer is waiting (writer-priority)
            while self._writer_active or self._writer_waiting_count > 0:
                self._readers_ok.wait()
            
            self._reader_count += 1

    def _read_release(self):
        """Releases the lock for reading."""
        with self._monitor:
            self._reader_count -= 1
            # If this is the *last* reader, and a writer is
            # waiting, notify the writer.
            if self._reader_count == 0 and self._writer_waiting_count > 0:
                self._writers_ok.notify()

    def _write_acquire(self):
        """Acquires the lock for writing."""
        with self._monitor:
            self._writer_waiting_count += 1
            
            # A writer must wait if any readers are active
            # OR if another writer is active
            while self._reader_count > 0 or self._writer_active:
                self._writers_ok.wait()
            
            self._writer_waiting_count -= 1
            self._writer_active = True

    def _write_release(self):
        """Releases the lock for writing."""
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
        """
        Provides a 'with' statement context for reading.
        Example:
            with lock.read():
                # read the shared data
        """
        self._read_acquire()
        try:
            yield
        finally:
            self._read_release()

    @contextmanager
    def write(self):
        """
        Provides a 'with' statement context for writing.
        Example:
            with lock.write():
                # write to the shared data
        """
        self._write_acquire()
        try:
            yield
        finally:
            self._write_release()
