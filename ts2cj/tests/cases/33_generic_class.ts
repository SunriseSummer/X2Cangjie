class Box<T> {
    inner: T;
    constructor(v: T) {
        this.inner = v;
    }
    read(): T {
        return this.inner;
    }
    write(v: T): void {
        this.inner = v;
    }
}

const b: Box<number> = new Box<number>(10);
console.log(b.read());
b.write(99);
console.log(b.read());
