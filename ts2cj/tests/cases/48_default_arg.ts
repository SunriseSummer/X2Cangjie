// 48 — Nullable parameter handling (default expression)
function greet(name: string, prefix: string = "Hello"): string {
    return prefix + ", " + name + "!";
}

console.log(greet("Alice"));
console.log(greet("Bob", "Hi"));
console.log(greet("Carol", "Greetings"));
