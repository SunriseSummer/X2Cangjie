// 45 — break / continue
let count: number = 0;
for (let i = 0; i < 100; i++) {
    if (i % 2 === 0) {
        continue;
    }
    if (i > 20) {
        break;
    }
    count = count + 1;
}
console.log(count); // odd numbers from 1..19  → 10

// nested with explicit flag (Cangjie has no labelled break)
let found: number = -1;
for (let i = 0; i < 10; i++) {
    if (found >= 0) {
        break;
    }
    for (let j = 0; j < 10; j++) {
        if (i * j === 24) {
            found = i * 100 + j;
            break;
        }
    }
}
console.log(found);

