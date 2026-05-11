// Optional chaining and nullish coalescing — TS-only syntax,
// expected to fall back to TODO comments for downstream AI to fix.
const v: number = 10;
const out: number = (v as number) ?? 0;
console.log(`out=${out}`);
