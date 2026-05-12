function identity<T>(x: T): T {
    return x;
}

function maxOf(a: number, b: number): number {
    if (a > b) return a;
    return b;
}

console.log(identity<number>(42));
console.log(identity<string>("hi"));
console.log(maxOf(3, 7));
