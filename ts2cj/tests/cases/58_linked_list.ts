// 58 — Singly-linked list of integers (sentinel-based, no `null`)
// Demonstrates: class with private fields, constructor, methods,
// while/for loops, recursion-like traversal, conditional logic, and
// using an Array<number> to back the list.  This avoids the
// TypeScript `null` pattern which has no zero-cost mapping in Cangjie
// (Option<T> requires pattern matching).

class IntList {
    // We store nodes in parallel arrays: data[i] is the value, next[i]
    // is the index of the next node, or -1 for end-of-list.  Free list
    // is tracked similarly via `freeHead`.
    private data: Array<number>;
    private next: Array<number>;
    private head: number;
    private len: number;
    private cap: number;
    private freeHead: number;

    constructor(cap: number) {
        this.cap = cap;
        this.head = -1;
        this.len = 0;
        this.freeHead = 0;
        this.data = new Array<number>(cap).fill(0);
        this.next = new Array<number>(cap).fill(0);
        for (let i = 0; i < cap - 1; i++) {
            this.next[i] = i + 1;
        }
        this.next[cap - 1] = -1;
    }

    private alloc(v: number): number {
        if (this.freeHead < 0) return -1;
        const idx: number = this.freeHead;
        this.freeHead = this.next[idx];
        this.data[idx] = v;
        this.next[idx] = -1;
        return idx;
    }

    private release(idx: number): void {
        this.next[idx] = this.freeHead;
        this.freeHead = idx;
    }

    size(): number {
        return this.len;
    }

    isEmpty(): boolean {
        return this.head < 0;
    }

    pushFront(v: number): void {
        const idx: number = this.alloc(v);
        if (idx < 0) return;
        this.next[idx] = this.head;
        this.head = idx;
        this.len = this.len + 1;
    }

    pushBack(v: number): void {
        const idx: number = this.alloc(v);
        if (idx < 0) return;
        if (this.head < 0) {
            this.head = idx;
        } else {
            let cur: number = this.head;
            while (this.next[cur] >= 0) {
                cur = this.next[cur];
            }
            this.next[cur] = idx;
        }
        this.len = this.len + 1;
    }

    popFront(): number {
        if (this.head < 0) return -1;
        const idx: number = this.head;
        const v: number = this.data[idx];
        this.head = this.next[idx];
        this.release(idx);
        this.len = this.len - 1;
        return v;
    }

    get(i: number): number {
        let cur: number = this.head;
        let k: number = 0;
        while (cur >= 0) {
            if (k === i) return this.data[cur];
            cur = this.next[cur];
            k = k + 1;
        }
        return -1;
    }

    contains(v: number): boolean {
        let cur: number = this.head;
        while (cur >= 0) {
            if (this.data[cur] === v) return true;
            cur = this.next[cur];
        }
        return false;
    }

    sum(): number {
        let total: number = 0;
        let cur: number = this.head;
        while (cur >= 0) {
            total = total + this.data[cur];
            cur = this.next[cur];
        }
        return total;
    }

    reverse(): void {
        let prev: number = -1;
        let cur: number = this.head;
        while (cur >= 0) {
            const nxt: number = this.next[cur];
            this.next[cur] = prev;
            prev = cur;
            cur = nxt;
        }
        this.head = prev;
    }

    printAll(): void {
        let cur: number = this.head;
        while (cur >= 0) {
            console.log(this.data[cur]);
            cur = this.next[cur];
        }
    }
}

function buildList(values: Array<number>): IntList {
    const list = new IntList(32);
    for (let i = 0; i < values.length; i++) {
        list.pushBack(values[i]);
    }
    return list;
}

const list = buildList([10, 20, 30, 40, 50]);
console.log(list.size());
console.log(list.get(0));
console.log(list.get(2));
console.log(list.get(4));
console.log(list.sum());
console.log(list.contains(30));
console.log(list.contains(99));

list.reverse();
console.log("-- after reverse --");
list.printAll();

list.popFront();
list.popFront();
console.log("-- after two popFront --");
console.log(list.size());
list.printAll();

list.pushFront(100);
list.pushFront(200);
console.log("-- after two pushFront --");
console.log(list.size());
list.printAll();

