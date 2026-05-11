// 29 — Static class member
class Util {
    static incBy(x: number, by: number): number {
        return x + by;
    }
}

console.log(Util.incBy(10, 5));
console.log(Util.incBy(0, 42));
