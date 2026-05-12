function safeDiv(a: number, b: number): number | null {
    if (b === 0) {
        return null;
    }
    return a / b;
}

const r1 = safeDiv(10, 2);
const r2 = safeDiv(10, 0);
switch (r1) {
    case null: console.log("r1=none"); break;
    default: console.log(r1);
}
switch (r2) {
    case null: console.log("r2=none"); break;
    default: console.log(r2);
}
