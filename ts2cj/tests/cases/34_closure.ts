// 34 — Closures: counter via class (Cangjie disallows returning a
// lambda that captures a *mutable* outer variable, so we wrap state
// in a small class — the idiomatic Cangjie equivalent of the JS
// counter-closure pattern.)
class Counter {
    n: number;
    constructor(start: number) {
        this.n = start;
    }
    next(): number {
        this.n = this.n + 1;
        return this.n;
    }
}

const c = new Counter(10);
console.log(c.next());
console.log(c.next());
console.log(c.next());

function makeAdder(by: number): (x: number) => number {
    return (x: number) => x + by;
}
const inc5 = makeAdder(5);
console.log(inc5(10));
console.log(inc5(20));

