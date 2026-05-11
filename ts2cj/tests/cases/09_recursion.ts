// 09 — Recursion
function factorial(n: number): number {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

function fib(n: number): number {
    if (n < 2) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

console.log(factorial(6));
console.log(fib(10));
