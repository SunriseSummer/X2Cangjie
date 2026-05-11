// 19 — Enum (numeric)
enum Color {
    Red,
    Green,
    Blue,
}

function colorName(c: Color): string {
    if (c == Color.Red) return "red";
    if (c == Color.Green) return "green";
    return "blue";
}

console.log(colorName(Color.Red));
console.log(colorName(Color.Green));
console.log(colorName(Color.Blue));
