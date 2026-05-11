// 53 — String building with template literals
function welcomeMsg(name: string, age: number, hobby: string): string {
    return `Hi, my name is ${name}, I am ${age} years old, and I like ${hobby}.`;
}

console.log(welcomeMsg("Ada", 30, "math"));
console.log(welcomeMsg("Bob", 25, "music"));

// nested expressions
const x: number = 10;
const y: number = 20;
console.log(`sum is ${x + y}, product is ${x * y}, doubled sum is ${(x + y) * 2}`);
