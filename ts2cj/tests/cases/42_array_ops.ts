// 42 — Array operations
const a: number[] = [3, 1, 4, 1, 5, 9, 2, 6];
console.log(a.length);
console.log(a[0]);
let sum: number = 0;
for (const x of a) {
    sum = sum + x;
}
console.log(sum);

let max: number = a[0];
for (let i = 1; i < a.length; i++) {
    if (a[i] > max) {
        max = a[i];
    }
}
console.log(max);

// reverse manually into a pre-sized array
const r: number[] = [0, 0, 0, 0, 0, 0, 0, 0];
for (let i = 0; i < a.length; i++) {
    r[i] = a[a.length - 1 - i];
}
for (const x of r) {
    console.log(x);
}

