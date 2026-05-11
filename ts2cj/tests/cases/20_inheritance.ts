class Animal {
    name: string;
    constructor(name: string) {
        this.name = name;
    }
    speak(): string {
        return "generic sound";
    }
}
class Dog extends Animal {
    constructor(name: string) {
        super(name);
    }
    speak(): string {
        return "woof";
    }
}
const a = new Animal("X");
const d = new Dog("Rex");
console.log(a.speak());
console.log(d.speak());
