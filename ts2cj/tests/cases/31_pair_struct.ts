// 31 — Tuple returning function (via small wrapper class)
class Pair {
    a: number;
    b: number;
    constructor(a: number, b: number) {
        this.a = a;
        this.b = b;
    }
}

function divmod(a: number, b: number): Pair {
    const q: number = Math.floor(a / b);
    const r: number = a - q * b;
    return new Pair(q, r);
}

const p = divmod(17, 5);
console.log(p.a);
console.log(p.b);


