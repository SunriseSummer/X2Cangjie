// 11 — Classes with constructor & methods
class Counter {
    count: number;
    constructor(start: number) {
        this.count = start;
    }
    incr(): void {
        this.count = this.count + 1;
    }
    value(): number {
        return this.count;
    }
}

const c: Counter = new Counter(10);
c.incr();
c.incr();
c.incr();
console.log(c.value());
