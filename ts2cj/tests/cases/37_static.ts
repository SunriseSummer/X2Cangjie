class MathUtil {
    static square(x: number): number {
        return x * x;
    }
    static cube(x: number): number {
        return x * x * x;
    }
}

console.log(MathUtil.square(5));
console.log(MathUtil.cube(3));
