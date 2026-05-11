// 32 — Properties via accessor methods
class Temperature {
    private c: number = 0;
    constructor(c: number) {
        this.c = c;
    }
    celsius(): number {
        return this.c;
    }
    setCelsius(v: number): void {
        this.c = v;
    }
    fahrenheit(): number {
        return this.c * 9 / 5 + 32;
    }
}

const t = new Temperature(100);
console.log(t.celsius());
console.log(t.fahrenheit());
t.setCelsius(0);
console.log(t.fahrenheit());

