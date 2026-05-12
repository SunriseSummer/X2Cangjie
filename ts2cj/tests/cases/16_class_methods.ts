class Counter {
    value: number;
    constructor(start: number) {
        this.value = start;
    }
    inc(): void {
        this.value = this.value + 1;
    }
    get(): number {
        return this.value;
    }
}
const c = new Counter(10);
c.inc();
c.inc();
c.inc();
console.log(`value=${c.get()}`);
