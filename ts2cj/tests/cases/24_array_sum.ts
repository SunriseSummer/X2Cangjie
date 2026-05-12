const xs: number[] = [3, 1, 4, 1, 5, 9, 2, 6];
let total: number = 0;
for (const x of xs) {
    total = total + x;
}
console.log(`total=${total}`);
