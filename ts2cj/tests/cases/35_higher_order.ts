// 35 — Higher-order: function returning function & taking function
function compose(f: (x: number) => number, g: (x: number) => number): (x: number) => number {
    return (x: number) => f(g(x));
}

function applyN(f: (x: number) => number, x: number, n: number): number {
    let r: number = x;
    for (let i = 0; i < n; i++) {
        r = f(r);
    }
    return r;
}

const double = (x: number) => x * 2;
const inc = (x: number) => x + 1;
const f = compose(double, inc);
console.log(f(3));           // (3+1)*2 = 8
console.log(applyN(inc, 0, 5));  // 5
console.log(applyN(double, 1, 4)); // 16
