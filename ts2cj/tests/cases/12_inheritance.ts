// 12 — Class inheritance
class Animal {
    name: string;
    constructor(n: string) {
        this.name = n;
    }
    speak(): string {
        return "generic sound";
    }
}

class Dog extends Animal {
    constructor(n: string) {
        super(n);
    }
    speak(): string {
        return "Woof!";
    }
}

const d: Dog = new Dog("Rex");
console.log(d.name);
console.log(d.speak());
