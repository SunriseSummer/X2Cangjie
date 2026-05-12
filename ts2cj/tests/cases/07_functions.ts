function add(a: number, b: number): number {
    return a + b;
}
function mul(a: number, b: number): number {
    return a * b;
}
const x: number = add(3, 4);
const y: number = mul(x, 2);
console.log(`x=${x} y=${y}`);
