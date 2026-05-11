// 55 — Queue (FIFO) implemented as a class
class Queue {
    private data: Array<number>;
    private head: number;
    private tail: number;
    private cap: number;
    constructor(cap: number) {
        this.cap = cap;
        this.head = 0;
        this.tail = 0;
        this.data = new Array<number>(cap).fill(0);
    }
    enqueue(x: number): boolean {
        if (this.tail - this.head >= this.cap) return false;
        this.data[this.tail % this.cap] = x;
        this.tail = this.tail + 1;
        return true;
    }
    dequeue(): number {
        if (this.head >= this.tail) return -1;
        const v: number = this.data[this.head % this.cap];
        this.head = this.head + 1;
        return v;
    }
    size(): number {
        return this.tail - this.head;
    }
}

const q = new Queue(16);
for (let i = 1; i <= 5; i++) {
    q.enqueue(i * 10);
}
console.log(q.size());
console.log(q.dequeue());
console.log(q.dequeue());
console.log(q.size());
q.enqueue(60);
console.log(q.size());
console.log(q.dequeue());
console.log(q.dequeue());
console.log(q.dequeue());
console.log(q.dequeue());
