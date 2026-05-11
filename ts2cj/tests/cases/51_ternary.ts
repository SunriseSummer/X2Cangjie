// 51 — Conditional expression (ternary)
function abs(n: number): number {
    return n < 0 ? -n : n;
}

function sign(n: number): number {
    return n > 0 ? 1 : (n < 0 ? -1 : 0);
}

console.log(abs(-7));
console.log(abs(7));
console.log(abs(0));
console.log(sign(-5));
console.log(sign(5));
console.log(sign(0));
