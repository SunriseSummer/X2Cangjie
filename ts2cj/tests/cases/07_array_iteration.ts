// 07 — Arrays and for-of iteration
const nums: number[] = [10, 20, 30, 40];
let s: number = 0;
for (const n of nums) {
    s = s + n;
}
console.log(s);
console.log(nums.length);
