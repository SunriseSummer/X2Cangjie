class Point {
    x: number;
    y: number;
    constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
    }
    sumSquares(): number {
        return this.x * this.x + this.y * this.y;
    }
}
const p = new Point(3, 4);
console.log(`r2=${p.sumSquares()}`);
