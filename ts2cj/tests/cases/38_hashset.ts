// 38 — HashSet via TS Set
const s: Set<string> = new Set<string>();
s.add("a");
s.add("b");
s.add("a");
console.log(s.size);
console.log(s.has("b"));
console.log(s.has("c"));
