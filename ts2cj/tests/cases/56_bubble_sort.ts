// 56 — Sorting: bubble sort on an Array
function bubbleSort(a: Array<number>): void {
    const n: number = a.length;
    for (let i = 0; i < n - 1; i++) {
        for (let j = 0; j < n - 1 - i; j++) {
            if (a[j] > a[j + 1]) {
                const tmp: number = a[j];
                a[j] = a[j + 1];
                a[j + 1] = tmp;
            }
        }
    }
}

const arr: Array<number> = [5, 2, 9, 1, 5, 6, 3, 8, 4, 7];
bubbleSort(arr);
for (const x of arr) {
    console.log(x);
}
