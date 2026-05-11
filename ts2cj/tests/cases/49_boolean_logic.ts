// 49 — Compound boolean logic (short-circuit)
function classify(n: number): string {
    if (n > 0 && n < 10) return "small positive";
    if (n >= 10 && n < 100) return "medium positive";
    if (n >= 100) return "large positive";
    if (n === 0) return "zero";
    return "negative";
}

console.log(classify(5));
console.log(classify(50));
console.log(classify(500));
console.log(classify(0));
console.log(classify(-7));

const a: boolean = true;
const b: boolean = false;
console.log(a && b);
console.log(a || b);
console.log(!a);
console.log(!b);
