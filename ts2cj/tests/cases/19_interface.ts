interface Greeter {
    hello(): string;
}
class English implements Greeter {
    hello(): string {
        return "hi";
    }
}
class Chinese implements Greeter {
    hello(): string {
        return "ni hao";
    }
}
const g1: Greeter = new English();
const g2: Greeter = new Chinese();
console.log(g1.hello());
console.log(g2.hello());
