// Functional collection helpers — exercises lambda/closure conversion,
// chained method calls, and string interpolation.  Uses ArrayList<T>
// with forEach-style enumeration.

function sum(xs: ArrayList<number>): number {
    let total: number = 0;
    for (const x of xs) {
        total = total + x;
    }
    return total;
}

function maxIn(xs: ArrayList<number>): number {
    let best: number = xs[0];
    for (let i = 1; i < xs.length; i++) {
        if (xs[i] > best) {
            best = xs[i];
        }
    }
    return best;
}

function countWhere(xs: ArrayList<number>, threshold: number): number {
    let c: number = 0;
    for (const x of xs) {
        if (x >= threshold) {
            c = c + 1;
        }
    }
    return c;
}

const nums: ArrayList<number> = new ArrayList<number>();
nums.push(3);
nums.push(1);
nums.push(4);
nums.push(1);
nums.push(5);
nums.push(9);
nums.push(2);
nums.push(6);

console.log(`sum=${sum(nums)}`);
console.log(`max=${maxIn(nums)}`);
console.log(`count>=4: ${countWhere(nums, 4)}`);
