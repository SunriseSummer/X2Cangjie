// 59 — Mid-sized program (~500 lines): a tiny stack-based calculator
// (Reverse Polish Notation evaluator) plus an infix→RPN converter
// (shunting-yard algorithm).  Exercises: classes, generics-like usage,
// arrays, while/for loops, switch-like dispatch, string operations,
// recursion, error handling, and a long main() with many call-sites.

class IntStack {
    private data: Array<number>;
    private top: number;
    private cap: number;
    constructor(cap: number) {
        this.cap = cap;
        this.top = 0;
        this.data = new Array<number>(cap).fill(0);
    }
    push(v: number): boolean {
        if (this.top >= this.cap) return false;
        this.data[this.top] = v;
        this.top = this.top + 1;
        return true;
    }
    pop(): number {
        if (this.top <= 0) return 0;
        this.top = this.top - 1;
        return this.data[this.top];
    }
    peek(): number {
        if (this.top <= 0) return 0;
        return this.data[this.top - 1];
    }
    size(): number {
        return this.top;
    }
    isEmpty(): boolean {
        return this.top === 0;
    }
    clear(): void {
        this.top = 0;
    }
}

class StringStack {
    private data: Array<string>;
    private top: number;
    private cap: number;
    constructor(cap: number) {
        this.cap = cap;
        this.top = 0;
        this.data = new Array<string>(cap).fill("");
    }
    push(v: string): boolean {
        if (this.top >= this.cap) return false;
        this.data[this.top] = v;
        this.top = this.top + 1;
        return true;
    }
    pop(): string {
        if (this.top <= 0) return "";
        this.top = this.top - 1;
        return this.data[this.top];
    }
    peek(): string {
        if (this.top <= 0) return "";
        return this.data[this.top - 1];
    }
    size(): number {
        return this.top;
    }
    isEmpty(): boolean {
        return this.top === 0;
    }
}

class StringQueue {
    private data: Array<string>;
    private head: number;
    private tail: number;
    private cap: number;
    constructor(cap: number) {
        this.cap = cap;
        this.head = 0;
        this.tail = 0;
        this.data = new Array<string>(cap).fill("");
    }
    enqueue(v: string): boolean {
        if (this.tail - this.head >= this.cap) return false;
        this.data[this.tail % this.cap] = v;
        this.tail = this.tail + 1;
        return true;
    }
    dequeue(): string {
        if (this.head >= this.tail) return "";
        const v: string = this.data[this.head % this.cap];
        this.head = this.head + 1;
        return v;
    }
    size(): number {
        return this.tail - this.head;
    }
    isEmpty(): boolean {
        return this.head >= this.tail;
    }
}

function isDigitChar(c: string): boolean {
    return c >= "0" && c <= "9";
}

function isOperatorChar(c: string): boolean {
    return c === "+" || c === "-" || c === "*" || c === "/" || c === "%";
}

function precedence(op: string): number {
    if (op === "+" || op === "-") return 1;
    if (op === "*" || op === "/" || op === "%") return 2;
    return 0;
}

function applyOp(op: string, a: number, b: number): number {
    if (op === "+") return a + b;
    if (op === "-") return a - b;
    if (op === "*") return a * b;
    if (op === "/") {
        if (b === 0) return 0;
        return Math.floor(a / b);
    }
    if (op === "%") {
        if (b === 0) return 0;
        return a - Math.floor(a / b) * b;
    }
    return 0;
}

// Tokeniser: convert a textual infix expression into a queue of tokens.
function tokenize(expr: string): StringQueue {
    const q = new StringQueue(256);
    const n: number = expr.length;
    let i: number = 0;
    while (i < n) {
        const c: string = expr.substring(i, i + 1);
        if (c === " " || c === "\t") {
            i = i + 1;
            continue;
        }
        if (isDigitChar(c)) {
            let j: number = i;
            while (j < n && isDigitChar(expr.substring(j, j + 1))) {
                j = j + 1;
            }
            q.enqueue(expr.substring(i, j));
            i = j;
            continue;
        }
        if (isOperatorChar(c) || c === "(" || c === ")") {
            q.enqueue(c);
            i = i + 1;
            continue;
        }
        // unknown character — skip
        i = i + 1;
    }
    return q;
}

// Convert tokens in infix order into RPN order using the shunting-yard
// algorithm.  Output is a fresh queue, input is consumed.
function infixToRpn(tokens: StringQueue): StringQueue {
    const out = new StringQueue(256);
    const ops = new StringStack(256);
    while (!tokens.isEmpty()) {
        const t: string = tokens.dequeue();
        // operand?
        if (isDigitChar(t.substring(0, 1))) {
            out.enqueue(t);
            continue;
        }
        if (t === "(") {
            ops.push(t);
            continue;
        }
        if (t === ")") {
            while (!ops.isEmpty() && ops.peek() !== "(") {
                out.enqueue(ops.pop());
            }
            if (!ops.isEmpty()) {
                ops.pop(); // discard "("
            }
            continue;
        }
        // operator
        while (!ops.isEmpty() && ops.peek() !== "("
                && precedence(ops.peek()) >= precedence(t)) {
            out.enqueue(ops.pop());
        }
        ops.push(t);
    }
    while (!ops.isEmpty()) {
        out.enqueue(ops.pop());
    }
    return out;
}

// Evaluate a queue of RPN tokens using an integer stack.
function evalRpn(rpn: StringQueue): number {
    const st = new IntStack(256);
    while (!rpn.isEmpty()) {
        const t: string = rpn.dequeue();
        if (isDigitChar(t.substring(0, 1))) {
            let v: number = 0;
            for (let i = 0; i < t.length; i++) {
                const ch: string = t.substring(i, i + 1);
                v = v * 10 + parseDigit(ch);
            }
            st.push(v);
            continue;
        }
        const b: number = st.pop();
        const a: number = st.pop();
        st.push(applyOp(t, a, b));
    }
    return st.pop();
}

function parseDigit(c: string): number {
    if (c === "0") return 0;
    if (c === "1") return 1;
    if (c === "2") return 2;
    if (c === "3") return 3;
    if (c === "4") return 4;
    if (c === "5") return 5;
    if (c === "6") return 6;
    if (c === "7") return 7;
    if (c === "8") return 8;
    if (c === "9") return 9;
    return 0;
}

function calc(expr: string): number {
    const toks = tokenize(expr);
    const rpn = infixToRpn(toks);
    return evalRpn(rpn);
}

// Recursive factorial — yet another tested feature.
function factorial(n: number): number {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Greatest common divisor (Euclidean algorithm).
function gcd(a: number, b: number): number {
    while (b !== 0) {
        const t: number = b;
        b = a - Math.floor(a / b) * b;
        a = t;
    }
    return a;
}

// LCM via gcd.
function lcm(a: number, b: number): number {
    if (a === 0 || b === 0) return 0;
    return Math.floor(a / gcd(a, b)) * b;
}

// Primality test via trial division.
function isPrime(n: number): boolean {
    if (n < 2) return false;
    if (n < 4) return true;
    if (n - Math.floor(n / 2) * 2 === 0) return false;
    let i: number = 3;
    while (i * i <= n) {
        if (n - Math.floor(n / i) * i === 0) return false;
        i = i + 2;
    }
    return true;
}

// Sum of digits, using the calculator's stack to be slightly elaborate.
function digitSum(n: number): number {
    let r: number = 0;
    let x: number = n;
    if (x < 0) {
        x = -x;
    }
    while (x > 0) {
        r = r + (x - Math.floor(x / 10) * 10);
        x = Math.floor(x / 10);
    }
    return r;
}

function fibonacci(n: number): number {
    if (n < 2) return n;
    let a: number = 0;
    let b: number = 1;
    for (let i = 2; i <= n; i++) {
        const c: number = a + b;
        a = b;
        b = c;
    }
    return b;
}

// ----- main: many tests -----
console.log("== calculator ==");
console.log(calc("1+2"));
console.log(calc("1 + 2 * 3"));
console.log(calc("(1 + 2) * 3"));
console.log(calc("10 - 4 - 3"));
console.log(calc("100 / 5 / 2"));
console.log(calc("2 + 3 * 4 - 5"));
console.log(calc("(2 + 3) * (4 - 1)"));
console.log(calc("7 % 3"));
console.log(calc("100 / 7"));

console.log("== factorial ==");
console.log(factorial(0));
console.log(factorial(1));
console.log(factorial(5));
console.log(factorial(8));

console.log("== gcd / lcm ==");
console.log(gcd(12, 18));
console.log(gcd(7, 13));
console.log(gcd(100, 75));
console.log(lcm(4, 6));
console.log(lcm(12, 18));
console.log(lcm(7, 13));

console.log("== primes ==");
console.log(isPrime(0));
console.log(isPrime(1));
console.log(isPrime(2));
console.log(isPrime(3));
console.log(isPrime(4));
console.log(isPrime(17));
console.log(isPrime(25));
console.log(isPrime(97));
console.log(isPrime(100));

console.log("== digit sum ==");
console.log(digitSum(0));
console.log(digitSum(7));
console.log(digitSum(12345));
console.log(digitSum(99999));

console.log("== fibonacci ==");
console.log(fibonacci(0));
console.log(fibonacci(1));
console.log(fibonacci(2));
console.log(fibonacci(5));
console.log(fibonacci(10));
console.log(fibonacci(15));

console.log("== stack ==");
const s = new IntStack(8);
s.push(1);
s.push(2);
s.push(3);
console.log(s.size());
console.log(s.peek());
console.log(s.pop());
console.log(s.pop());
console.log(s.size());
console.log(s.isEmpty());
console.log(s.pop());
console.log(s.isEmpty());
