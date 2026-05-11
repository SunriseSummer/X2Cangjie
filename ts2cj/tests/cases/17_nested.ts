function sumUpTo(n: number): number {
    let total: number = 0;
    for (let i = 1; i < n + 1; i++) {
        total = total + i;
    }
    return total;
}
console.log(`sum(1..10) = ${sumUpTo(10)}`);
