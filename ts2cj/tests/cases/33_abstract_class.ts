// 33 — Abstract class & polymorphism
abstract class Shape {
    abstract area(): number;
    describe(): string {
        const a: number = this.area();
        return "Shape with area " + a;
    }
}

class Circle extends Shape {
    r: number;
    constructor(r: number) {
        super();
        this.r = r;
    }
    area(): number {
        return 3 * this.r * this.r;
    }
}

class Square extends Shape {
    s: number;
    constructor(s: number) {
        super();
        this.s = s;
    }
    area(): number {
        return this.s * this.s;
    }
}

const shapes: Shape[] = [new Circle(2), new Square(3)];
for (const s of shapes) {
    console.log(s.describe());
}

