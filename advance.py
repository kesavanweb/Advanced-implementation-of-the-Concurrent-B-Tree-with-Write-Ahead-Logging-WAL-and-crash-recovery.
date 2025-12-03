import threading
import json
import os
import time
import random

# ================= WAL ======================

class WAL:
    def __init__(self, filename="wal.log"):
        self.filename = filename
        self.lock = threading.Lock()
        open(self.filename, 'a').close()

    def log(self, record):
        with self.lock:
            with open(self.filename, 'a') as f:
                f.write(json.dumps(record) + "\n")
                f.flush()
                os.fsync(f.fileno())

    def recover(self):
        operations = []
        if not os.path.exists(self.filename):
            return operations

        with open(self.filename, 'r') as f:
            for line in f:
                operations.append(json.loads(line))
        return operations

    def clear(self):
        open(self.filename, 'w').close()


# ================= B-TREE NODE ======================

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t
        self.leaf = leaf
        self.keys = []
        self.children = []
        self.lock = threading.Lock()

    def is_full(self):
        return len(self.keys) == (2 * self.t - 1)


# ================= B-TREE ======================

class ConcurrentBTree:
    def __init__(self, t, wal):
        self.t = t
        self.root = BTreeNode(t, True)
        self.wal = wal
        self.tree_lock = threading.Lock()

    # ---------------- SEARCH ----------------
    def search(self, key, node=None):
        if node is None:
            node = self.root

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            return True

        if node.leaf:
            return False

        return self.search(key, node.children[i])

    # ---------------- SPLIT -----------------
    def split_child(self, parent, i, child):
        t = self.t
        new = BTreeNode(t, child.leaf)

        new.keys = child.keys[t:]
        mid = child.keys[t - 1]
        child.keys = child.keys[:t - 1]

        if not child.leaf:
            new.children = child.children[t:]
            child.children = child.children[:t]

        parent.keys.insert(i, mid)
        parent.children.insert(i + 1, new)

    # ---------------- INSERT ----------------
    def insert(self, key):
        # WAL FIRST !
        self.wal.log({"op": "insert", "key": key})

        with self.tree_lock:
            root = self.root

            if root.is_full():
                new_root = BTreeNode(self.t)
                new_root.children.append(self.root)
                self.split_child(new_root, 0, root)
                self.root = new_root
                self._insert_non_full(new_root, key)
            else:
                self._insert_non_full(root, key)

    def _insert_non_full(self, node, key):
        with node.lock:
            if node.leaf:
                node.keys.append(key)
                node.keys.sort()
            else:
                i = len(node.keys) - 1
                while i >= 0 and key < node.keys[i]:
                    i -= 1
                i += 1

                child = node.children[i]
                if child.is_full():
                    self.split_child(node, i, child)
                    if key > node.keys[i]:
                        i += 1

                self._insert_non_full(node.children[i], key)

    # ---------------- RECOVERY ----------------
    def recover(self):
        print("\n[RECOVERY] Replaying WAL...")
        logs = self.wal.recover()
        for entry in logs:
            if entry["op"] == "insert":
                self._recovery_insert(entry["key"])

    def _recovery_insert(self, key):
        root = self.root
        if root.is_full():
            new_root = BTreeNode(self.t)
            new_root.children.append(root)
            self.split_child(new_root, 0, root)
            self.root = new_root

        self._insert_non_full(self.root, key)

    # ---------------- DISPLAY ----------------
    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root

        print(" " * level * 4 + str(node.keys))
        for child in node.children:
            self.print_tree(child, level + 1)


# ================= TESTING ======================

def worker(tree, tid):
    for _ in range(10):
        key = random.randint(1, 100)
        print(f"[Thread {tid}] inserting {key}")
        tree.insert(key)
        time.sleep(random.random() * 0.1)


def simulate_crash():
    print("\n--- CRASH SIMULATED ---\n")
    exit(1)


# ================= MAIN ======================

if __name__ == "__main__":
    wal = WAL()
    wal.clear()

    print("Starting B-Tree with WAL...")
    tree = ConcurrentBTree(t=3, wal=wal)

    threads = []

    for i in range(3):
        t = threading.Thread(target=worker, args=(tree, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\nTREE BEFORE CRASH:")
    tree.print_tree()

    # Simulate crash by stopping program manually here
    print("\nSimulating crash... Restart program to test recovery.")
    # simulate_crash()

    # ---------------- RESTART BLOCK ----------------
    print("\nRESTARTING SYSTEM...\n")
    new_tree = ConcurrentBTree(3, wal)
    new_tree.recover()

    print("\nTREE AFTER RECOVERY:")
    new_tree.print_tree()

    # Test Search
    test_val = random.randint(1, 100)
    print(f"\nSearching for {test_val}:", new_tree.search(test_val))
