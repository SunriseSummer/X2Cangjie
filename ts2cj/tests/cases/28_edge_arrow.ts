// Arrow function bound to a variable — converter has a pattern but
// Cangjie lambda syntax differs subtly; demonstrates a typical "small
// detail error" that the downstream AI pass would fix.
const add = (a: number, b: number) => a + b;
console.log(`${add(2, 3)}`);
