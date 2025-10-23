# Reader-Writer Lock

This project is a Python implementation of the classic **Reader-Writer Concurrency Problem** for an Operating Systems course. It provides three different lock implementations using only the built-in `threading` module, each demonstrating a different priority strategy.

The core of the project is a set of self-contained Reader-Writer Lock classes that use `threading.Lock` and `threading.Condition` variables to safely coordinate concurrent access to a shared resource.

## The Reader-Writer Problem

In many applications, a shared resource (like a file or data buffer) is accessed by multiple threads.
* **Readers:** Only read the data. They do not modify it.
* **Writers:** Modify the data.

To ensure data integrity, we must follow these rules:
1.  Any number of **Readers** can access the resource at the same time.
2.  A **Writer** must have *exclusive* access. No other writer or reader can be in the critical section at the same time.

## How It Works: The Three Priority Models

This project implements all three classic solutions to the problem, each with different performance trade-offs.

### 1. Reader-Priority (`ReaderPriorityRWLock`)
This is the simplest solution.
* **Logic:** As long as at least one reader is in the critical section, all other readers are allowed to enter. A writer can only get the lock when the resource is completely empty.
* **Trade-off:** This is great for read-heavy applications but can lead to **Writer Starvation**. A constant stream of new readers can make a writer wait indefinitely.

### 2. Writer-Priority (`WriterPriorityRWLock`)
This solution gives preference to writers to prevent their starvation.
* **Logic:** If a writer is waiting to get the lock, all *new* readers are blocked (they must wait). Once the last active reader leaves, the waiting writer gets the lock.
* **Trade-off:** This solves writer starvation, but can cause **Reader Starvation** if a constant stream of writers arrives.

### 3. Fair (FIFO) Priority (`FairRWLock`)
This is the most complex but "fair" solution.
* **Logic:** Access is granted in a first-come, first-served (FIFO) order. All waiting threads (both readers and writers) are put in a single conceptual queue. When the lock is released, the thread(s) at the front of the queue are allowed to proceed.
* **Trade-off:** This prevents both reader and writer starvation, but the overhead is slightly higher. If a group of readers arrives, followed by a writer, followed by more readers, the writer will have to wait for the first group of readers, but the *second* group of readers will have to wait for the writer.

## Features

* **Three Implementations:** Provides `ReaderPriorityRWLock`, `WriterPriorityRWLock`, and `FairRWLock` in a single package.
* **Self-Contained Classes:** The locks are completely decoupled and can protect any shared resource.
* **Context Manager:** All three classes implement the *same* `.read()` and `.write()` context managers (`with` statement). This ensures the lock is *always* released, even if an exception occurs, and makes them interchangeable.
* **Modular Package:** All lock logic is encapsulated in the `rw_lock/` package.
* **CLI Simulator:** The `main.py` script provides a configurable simulator to test and observe the behavior of each lock type.

## Project Structure

```
python-reader-writer-lock/
├── .gitignore
├── LICENSE
├── README.md                # This documentation
├── main.py                  # Main runnable script (CLI)
└── rw_lock/
    ├── __init__.py          # Makes 'rw_lock' a package
    └── locks.py             # The three RWLock class implementations
```

## How to Run

The project uses only built-in Python modules.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/msmrexe/python-reader-writer-lock.git
    cd python-reader-writer-lock
    ```
2.  **Run the simulation:**
    Run `main.py` from your terminal. Use the `--priority` flag to select which lock to test.

    ```bash
    # Test the default Writer-Priority lock
    python main.py
    
    # Test the Reader-Priority lock (try with high write prob)
    python main.py --priority reader --num-threads 20 --write-prob 0.5
    
    # Test the Fair (FIFO) lock
    python main.py --priority fair
    
    # Run a simulation with many readers
    python main.py --priority writer --num-threads 20 --write-prob 0.1
    ```
    
    You will see the log output in your terminal, showing how the threads wait and access the resource one by one (writers) or in groups (readers). By changing the priority, you can observe the different behaviors.
    
---

## Author

Feel free to connect or reach out if you have any questions!

* **Maryam Rezaee**
* **GitHub:** [@msmrexe](https://github.com/msmrexe)
* **Email:** [ms.maryamrezaee@gmail.com](mailto:ms.maryamrezaee@gmail.com)

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.
