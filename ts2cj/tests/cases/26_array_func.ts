// 26 — Multiple top-level declarations and a function with array argument
function sumArray(a: number[]): number {
    let s: number = 0;
    for (const v of a) {
        s = s + v;
    }
    return s;
}

const nums: number[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
console.log(sumArray(nums));
