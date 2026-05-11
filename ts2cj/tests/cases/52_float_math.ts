// 52 — Float computation (Float64)
function area(r: number): number {
    return 3.14159265 * r * r;
}

function distance(x1: number, y1: number, x2: number, y2: number): number {
    const dx: number = x2 - x1;
    const dy: number = y2 - y1;
    return Math.sqrt(dx * dx + dy * dy);
}

console.log(area(1.0));
console.log(area(2.5));
console.log(distance(0.0, 0.0, 3.0, 4.0));
console.log(distance(1.0, 1.0, 4.0, 5.0));
