function fact(n: number): number {
    if (n <= 1) {
        return 1;
    }
    return n * fact(n - 1);
}
console.log(`5! = ${fact(5)}`);
