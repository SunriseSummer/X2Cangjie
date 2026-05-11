// 10 — Arrow functions & higher-order
const double = (x: number): number => x * 2;
const inc = (x: number): number => x + 1;
console.log(double(5));
console.log(inc(9));

function apply(f: (n: number) => number, v: number): number {
    return f(v);
}
console.log(apply(double, 21));
