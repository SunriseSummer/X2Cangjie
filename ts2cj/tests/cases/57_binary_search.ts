// 57 — Binary search
function binarySearch(a: Array<number>, target: number): number {
    let lo: number = 0;
    let hi: number = a.length - 1;
    while (lo <= hi) {
        const mid: number = (lo + hi) / 2;
        const m: number = Math.floor(mid);
        if (a[m] === target) {
            return m;
        }
        if (a[m] < target) {
            lo = m + 1;
        } else {
            hi = m - 1;
        }
    }
    return -1;
}

const a: Array<number> = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25];
console.log(binarySearch(a, 1));
console.log(binarySearch(a, 25));
console.log(binarySearch(a, 13));
console.log(binarySearch(a, 14));
console.log(binarySearch(a, 100));
