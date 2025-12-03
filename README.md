# Advanced-implementation-of-the-Concurrent-B-Tree-with-Write-Ahead-Logging-WAL-and-crash-recovery.
Starting B-Tree with WAL...
[Thread 0] inserting 10
[Thread 1] inserting 40
[Thread 2] inserting 17
[Thread 0] inserting 97
[Thread 2] inserting 63
[Thread 1] inserting 95
[Thread 0] inserting 17[Thread 1] inserting 20

[Thread 0] inserting 98
[Thread 1] inserting 57
[Thread 2] inserting 34
[Thread 1] inserting 12
[Thread 2] inserting 70
[Thread 0] inserting 29
[Thread 2] inserting 53
[Thread 1] inserting 38
[Thread 0] inserting 48
[Thread 1] inserting 59
[Thread 2] inserting 35
[Thread 1] inserting 57
[Thread 0] inserting 27
[Thread 1] inserting 81
[Thread 2] inserting 36
[Thread 0] inserting 79
[Thread 0] inserting 60
[Thread 1] inserting 33
[Thread 2] inserting 46
[Thread 2] inserting 52
[Thread 0] inserting 42
[Thread 2] inserting 68

TREE BEFORE CRASH:
[40]
    [17, 34]
        [10, 12, 17]
        [20, 27, 29, 33]
        [35, 36, 38]
    [57, 63, 95]
        [42, 46, 48, 52, 53]
        [57, 59, 60]
        [68, 70, 79, 81]
        [97, 98]

Simulating crash... Restart program to test recovery.

RESTARTING SYSTEM...


[RECOVERY] Replaying WAL...

TREE AFTER RECOVERY:
[40]
    [17, 34]
        [10, 12, 17]
        [20, 27, 29, 33]
        [35, 36, 38]
    [57, 63, 95]
        [42, 46, 48, 52, 53]
        [57, 59, 60]
        [68, 70, 79, 81]
        [97, 98]

Searching for 2: False
