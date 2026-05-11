// 17 — switch → match
function describe(n: number): string {
    switch (n) {
        case 0:
            return "zero";
        case 1:
            return "one";
        case 2:
            return "two";
        default:
            return "many";
    }
}

console.log(describe(0));
console.log(describe(1));
console.log(describe(2));
console.log(describe(7));
