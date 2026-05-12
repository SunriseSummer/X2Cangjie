abstract class Shape {
    abstract area(): number;
    describe(): string {
        return `area=${this.area()}`;
    }
}

class Square extends Shape {
    side: number;
    constructor(side: number) {
        super();
        this.side = side;
    }
    area(): number {
        return this.side * this.side;
    }
}

const s: Shape = new Square(4);
console.log(s.describe());
