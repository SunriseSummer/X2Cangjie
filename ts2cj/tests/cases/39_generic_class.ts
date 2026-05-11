// 39 — Generic class
class Box<T> {
    value: T;
    constructor(v: T) {
        this.value = v;
    }
    get(): T {
        return this.value;
    }
    set(v: T): void {
        this.value = v;
    }
}

const ib: Box<number> = new Box<number>(10);
console.log(ib.get());
ib.set(20);
console.log(ib.get());

const sb: Box<string> = new Box<string>("hi");
console.log(sb.get());
