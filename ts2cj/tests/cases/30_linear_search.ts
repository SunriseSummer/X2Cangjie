// 30 — Comprehensive: small algorithm (linear search)
function indexOf(arr: number[], target: number): number {
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] === target) {
            return i;
        }
    }
    return -1;
}

const a: number[] = [10, 20, 30, 40, 50];
console.log(indexOf(a, 30));
console.log(indexOf(a, 99));
