// 40 — Static methods & fields
class MathUtil {
    static PI: number = 3;
    static double(x: number): number {
        return x * 2;
    }
    static cube(x: number): number {
        return x * x * x;
    }
}

console.log(MathUtil.PI);
console.log(MathUtil.double(7));
console.log(MathUtil.cube(3));
