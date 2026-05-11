// A small program that demonstrates several features together.
function double(x: number): number {
    return x * 2;
}
class Box {
    value: number;
    constructor(v: number) {
        this.value = v;
    }
    show(): void {
        console.log(`box=${this.value}`);
    }
}
const b = new Box(double(7));
b.show();
