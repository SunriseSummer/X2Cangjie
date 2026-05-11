// 24 — Default-value parameter
function greet(name: string, prefix: string = "Hello"): string {
    return prefix + ", " + name;
}
console.log(greet("Alice"));
console.log(greet("Bob", "Hi"));
