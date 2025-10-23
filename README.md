# Python Reader-Writer Lock

This project is a Python implementation of the classic **Reader-Writer Concurrency Problem** for an Operating Systems course. It provides a **Writer-Priority Reader-Writer Lock** using only the built-in `threading` module.

The core of the project is a self-contained `WriterPriorityRWLock` class that uses `threading.Lock` and `threading.Condition` variables to safely coordinate concurrent access to a shared resource.

## The Reader-Writer Problem

In many applications, a shared resource (like a file or data buffer) is accessed by multiple threads.
* **Readers:** Only read the data. They do not modify it.
* **Writers:** Modify the data.

To ensure data integrity, we must follow these rules:
1.  Any number of **Readers** can access the resource at the same time.
2.  A **Writer** must have *exclusive* access. No other writer or reader can be in the critical section at the same time.

## How It Works: A Writer-Priority Solution

This implementation gives *priority to waiting writers*. If a writer thread is waiting to access the resource, all *new* reader threads will be blocked until the writer has had its turn. This prevents a constant stream of readers from starving the writers.

The `WriterPriorityRWLock` class manages this logic internally.

### 1. State Variables
The lock maintains its own internal state, protected by a single `threading.Lock` (monitor):
* `_reader_count`: How many readers are *currently* in the critical section.
* `_writer_active`: A boolean, `True` if a writer is *currently* in the critical section.
* `_writer_waiting_count`: How many writers are *waiting* to get the lock.

### 2. Condition Variables
Two `threading.Condition` variables are used to signal threads:
* `_readers_ok`: Readers wait on this.
* `_writers_ok`: Writers wait on this.

### 3. Logic
* **Reader Acquires (`lock.read()`):**
    A new reader is only allowed to enter if:
    1.  No writer is currently active (`_writer_active == False`).
    2.  AND no writers are waiting (`_writer_waiting_count == 0`).
    If not, it waits on `_readers_ok`.

* **Writer Acquires (`lock.write()`):**
    A new writer increments `_writer_waiting_count` and then waits until:
    1.  No readers are active (`_reader_count == 0`).
    2.  AND no other writer is active (`_writer_active == False`).
    If not, it waits on `_writers_ok`.

* **Reader Releases:**
    The reader decrements `_reader_count`. If it is the *last* reader (`_reader_count == 0`) and writers are waiting, it signals *one* waiting writer using `_writers_ok.notify()`.

* **Writer Releases:**
    The writer sets `_writer_active = False`. It then gives priority to another waiting writer by first checking `_writer_waiting_count`.
    1.  If writers are waiting, it signals *one* writer: `_writers_ok.notify()`.
    2.  If *no* writers are waiting, it signals *all* waiting readers: `_readers_ok.notify_all()`.

## Features

* **Self-Contained Class:** The `WriterPriorityRWLock` is completely decoupled and can protect any shared resource.
* **Context Manager:** Implements `lock.read()` and `lock.write()` as context managers (`with` statement). This ensures the lock is *always* released, even if an exception occurs.
* **Writer-Priority:** Prevents writer starvation.
* **Modular Package:** All lock logic is encapsulated in the `rw_lock/` package.
* **CLI Simulator:** The `main.py` script provides a configurable simulator to test the lock with a variable number of reader and writer threads.

## Project Structure

```
python-reader-writer-lock/
├── .gitignore
├── LICENSE
├── README.md                # This documentation
├── main.py                  # Main runnable script (CLI)
└── rw_lock/
    ├── __init__.py          # Makes 'rw_lock' a package
    └── lock.py              # The WriterPriorityRWLock class
```

## How to Run

The project uses only built-in Python modules.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/msmrexe/python-reader-writer-lock.git
    cd python-reader-writer-lock
    ```
2.  **Run the simulation:**
    Run `main.py` from your terminal. You can use flags to configure the simulation.

    ```bash
    # Run with default settings (10 threads, 30% writer probability)
    python main.py
    
    # Run a simulation with many readers and few writers
    python main.py --num-threads 20 --write-prob 0.1
    
    # Run with a high contention for writing
    python main.py --num-threads 10 --write-prob 0.8
    ```
    
    You will see the log output in your terminal, showing how the threads wait and access the resource one by one (writers) or in groups (readers).
    
---

## Author

Feel free to connect or reach out if you have any questions!

* **Maryam Rezaee**
* **GitHub:** [@msmrexe](https://github.com/msmrexe)
* **Email:** [ms.maryamrezaee@gmail.com](mailto:ms.maryamrezaee@gmail.com)

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.
