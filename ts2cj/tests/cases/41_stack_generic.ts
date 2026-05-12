// Medium-sized test (~80 lines): a generic stack with helpful queries.
// Demonstrates: generic class, fields, init via explicit constructor,
// optional return (`T | null`), top-level use, switch-as-match.
//
// We follow Cangjie collection naming (``add`` rather than the TS
// ``push``) so the generated code reads naturally.

class Stack<T> {
    data: T[];
    constructor() {
        this.data = new Array<T>();
    }
    add(v: T): void {
        this.data.push(v);
    }
    peek(): T | null {
        if (this.data.length === 0) {
            return null;
        }
        return this.data[this.data.length - 1];
    }
    size(): number {
        return this.data.length;
    }
    isEmpty(): boolean {
        return this.data.length === 0;
    }
}

function sumStack(s: Stack<number>): number {
    let total: number = 0;
    for (let i = 0; i < s.size(); i++) {
        total = total + s.data[i];
    }
    return total;
}

function describe(s: Stack<number>): string {
    if (s.isEmpty()) {
        return "stack=[]";
    }
    let out: string = "stack=[";
    for (let i = 0; i < s.size(); i++) {
        if (i > 0) {
            out = out + ",";
        }
        out = out + `${s.data[i]}`;
    }
    out = out + "]";
    return out;
}

const s: Stack<number> = new Stack<number>();
s.add(1);
s.add(2);
s.add(3);
s.add(4);
s.add(5);
console.log(describe(s));
console.log(`size=${s.size()}`);
console.log(`sum=${sumStack(s)}`);

switch (s.peek()) {
    case null: console.log("peek=none"); break;
    default: console.log(`peek=${s.peek()}`);
}

const empty: Stack<number> = new Stack<number>();
console.log(describe(empty));
console.log(`isEmpty=${empty.isEmpty()}`);
