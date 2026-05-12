struct Point {
    x: number = 0;
    y: number = 0;
    constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
    }
}

const p: Point = new Point(3, 4);
console.log(`p=(${p.x},${p.y})`);
