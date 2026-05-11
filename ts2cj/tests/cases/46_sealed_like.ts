// 46 — Class hierarchy with `instanceof` checks (`is` in Cangjie)
class Animal {
    name: string;
    constructor(n: string) {
        this.name = n;
    }
    kind(): string {
        return "Animal";
    }
}

class Dog extends Animal {
    constructor(n: string) {
        super(n);
    }
    kind(): string {
        return "Dog";
    }
}

class Cat extends Animal {
    constructor(n: string) {
        super(n);
    }
    kind(): string {
        return "Cat";
    }
}

class Cow extends Animal {
    constructor(n: string) {
        super(n);
    }
    kind(): string {
        return "Cow";
    }
}

function describe(a: Animal): string {
    if (a instanceof Dog) return a.name + " is a dog";
    if (a instanceof Cat) return a.name + " is a cat";
    if (a instanceof Cow) return a.name + " is a cow";
    return a.name + " is some animal";
}

const animals: Animal[] = [
    new Dog("Rex"),
    new Cat("Whiskers"),
    new Cow("Bessie"),
];

for (const a of animals) {
    console.log(describe(a));
}

