// 13 — Interface + class implementing it
interface Greeter {
    greet(): string;
}

class Hello implements Greeter {
    name: string;
    constructor(n: string) {
        this.name = n;
    }
    greet(): string {
        return "Hi, " + this.name;
    }
}

const h: Hello = new Hello("Sam");
console.log(h.greet());
