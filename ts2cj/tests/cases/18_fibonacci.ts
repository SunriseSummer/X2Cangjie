function fib(n: number): number {
    if (n < 2) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}
for (let i = 0; i < 8; i++) {
    console.log(`fib(${i}) = ${fib(i)}`);
}
