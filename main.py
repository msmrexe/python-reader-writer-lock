# main.py

"""
Reader-Writer Problem Simulator

This script spawns a number of concurrent reader and writer
threads to demonstrate the three types of RW Locks.
"""

import threading
import logging
import random
import time
import argparse
# Import all three lock classes from the 'locks' module
from rw_lock.locks import (
    ReaderPriorityRWLock, 
    WriterPriorityRWLock, 
    FairRWLock
)

# --- Global Shared Resources ---
shared_buffer = []
lock = None # Will be set in main()

# ---------------------------------
# Thread Target Functions
# ---------------------------------

def writer(name: str):
    """
    The target function for writer threads.
    Acquires a write lock and appends to the buffer.
    """
    logging.info('is waiting to write...')
    
    with lock.write():
        # --- Start Critical Section ---
        logging.info('is starting to write.')
        
        value = random.randint(1, 100)
        shared_buffer.append(value)
        logging.info(f'WROTE: {value} (Buffer: {shared_buffer})')
        
        # Simulate work
        time.sleep(random.uniform(0.1, 0.3))
        
        logging.info('is finishing writing.')
        # --- End Critical Section ---

def reader(name: str):
    """
    The target function for reader threads.
    Acquires a read lock and reads from the buffer.
    """
    logging.info('is waiting to read...')
    
    with lock.read():
        # --- Start Critical Section ---
        logging.info('is starting to read.')
        
        # Simulate work
        time.sleep(random.uniform(0.1, 0.3))
        
        if not shared_buffer:
            logging.info('READ: Buffer is empty.')
        else:
            logging.info(f'READ: Buffer state is {shared_buffer}')
            
        logging.info('is finishing reading.')
        # --- End Critical Section ---

# ---------------------------------
# Main Simulator Setup
# ---------------------------------

def main():
    """Parses args and runs the simulation."""
    global lock # We need to assign the global 'lock'
    
    parser = argparse.ArgumentParser(
        description="Run a Reader-Writer lock simulation."
    )
    parser.add_argument(
        '-t', '--num-threads',
        type=int,
        default=10,
        help="Total number of threads to spawn."
    )
    parser.add_argument(
        '-w', '--write-prob',
        type=float,
        default=0.3,
        help="Probability (0.0 to 1.0) of a thread being a writer."
    )
    parser.add_argument(
        '-p', '--priority',
        choices=['reader', 'writer', 'fair'],
        default='writer',
        help="Set the lock priority model."
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO'],
        default='INFO',
        help="Set the logging level."
    )
    args = parser.parse_args()

    # --- Setup Logging ---
    log_level = logging.DEBUG if args.log_level == 'DEBUG' else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='{threadName} {message}',
        style='{'
    )
    
    # --- Select and instantiate the chosen lock ---
    if args.priority == 'reader':
        lock = ReaderPriorityRWLock()
    elif args.priority == 'writer':
        lock = WriterPriorityRWLock()
    elif args.priority == 'fair':
        lock = FairRWLock()

    print(f"--- Starting {args.priority.title()}-Priority Simulation ---")
    
    # --- Start Simulation ---
    threads = []
    wcount, rcount = 0, 0

    print(f"Starting {args.num_threads} threads. Writer probability: {args.write_prob*100}%")
    
    for i in range(args.num_threads):
        if random.random() < args.write_prob:
            # Create a Writer
            wcount += 1
            name = f'Writer-{wcount}'
            target = writer
        else:
            # Create a Reader
            rcount += 1
            name = f'Reader-{rcount}'
            target = reader
            
        thread = threading.Thread(target=target, name=name, args=(name,))
        threads.append(thread)
        
        logging.info(f'Starting {name}...')
        thread.start()
        time.sleep(random.uniform(0, 0.1)) # Stagger thread starts

    # --- Wait for all threads to complete ---
    for thread in threads:
        thread.join()
        
    print("All threads finished.")
    print(f"Final Buffer State: {shared_buffer}")

if __name__ == "__main__":
    main()
