// 54 — Comprehensive: stack implemented with an Array
class Stack {
    private data: Array<number>;
    private top: number;
    private cap: number;
    constructor(cap: number) {
        this.cap = cap;
        this.top = 0;
        this.data = new Array<number>(cap).fill(0);
    }
    push(x: number): boolean {
        if (this.top >= this.cap) return false;
        this.data[this.top] = x;
        this.top = this.top + 1;
        return true;
    }
    pop(): number {
        if (this.top <= 0) return -1;
        this.top = this.top - 1;
        return this.data[this.top];
    }
    size(): number {
        return this.top;
    }
    peek(): number {
        if (this.top <= 0) return -1;
        return this.data[this.top - 1];
    }
}

const st = new Stack(8);
st.push(10);
st.push(20);
st.push(30);
console.log(st.size());
console.log(st.peek());
console.log(st.pop());
console.log(st.pop());
console.log(st.size());
console.log(st.peek());
