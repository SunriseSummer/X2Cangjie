// 27 — instanceof / typeof narrowing
function describe(v: number | string): string {
    if (typeof v === "number") {
        return "num";
    }
    return "str";
}

console.log(describe(7));
console.log(describe("hi"));
