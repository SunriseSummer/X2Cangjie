// Generic function — TS generics ≈ Cangjie generics but with different
// surface syntax. Expect partial accuracy.
function identity<T>(x: T): T {
    return x;
}
console.log(`${identity(42)}`);
