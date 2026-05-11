// 36 — Mutual recursion
function isEven(n: number): boolean {
    if (n === 0) return true;
    return isOdd(n - 1);
}

function isOdd(n: number): boolean {
    if (n === 0) return false;
    return isEven(n - 1);
}

console.log(isEven(0));
console.log(isEven(7));
console.log(isOdd(7));
console.log(isEven(12));
