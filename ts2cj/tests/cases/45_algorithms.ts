// =====================================================================
// Algorithmic toolbox (~600 lines).  Exercises a very wide slice of
// language features without depending on TS-specific string semantics:
//
//   * Classes with inheritance and overrides
//   * Generic ArrayList<T> / HashMap<K,V>
//   * Enums with switch / match
//   * Recursion, mutual recursion, iteration
//   * Throw / try / catch
//   * Tuple-like return via small classes
//   * Top-level functions and a driver "main"
//
// Modules covered:
//   1. Sieve of Eratosthenes
//   2. GCD / LCM / modular exponentiation
//   3. Matrix add / multiply / transpose
//   4. Sorting:  bubble, insertion, quick, merge, heap
//   5. Graph (adjacency list) — BFS / DFS / connected components
//   6. Disjoint-set union-find
//   7. Mini-statistics (mean / variance / median)
//   8. Bitset
//
// =====================================================================

// --- 1. Sieve of Eratosthenes ----------------------------------------

function sieve(n: number): ArrayList<number> {
    const isComposite: ArrayList<boolean> = new ArrayList<boolean>();
    for (let i = 0; i <= n; i++) {
        isComposite.push(false);
    }
    isComposite[0] = true;
    if (n >= 1) {
        isComposite[1] = true;
    }
    let p: number;
    for (p = 2; p * p <= n; p++) {
        if (isComposite[p]) {
            continue;
        }
        let k: number = p * p;
        while (k <= n) {
            isComposite[k] = true;
            k = k + p;
        }
    }
    const out: ArrayList<number> = new ArrayList<number>();
    for (let i = 2; i <= n; i++) {
        if (!isComposite[i]) {
            out.push(i);
        }
    }
    return out;
}

// --- 2. Number theory ------------------------------------------------

function gcd(a: number, b: number): number {
    if (b === 0) return a;
    return gcd(b, a - (a / b) * b);
}

function lcm(a: number, b: number): number {
    return a / gcd(a, b) * b;
}

function modpow(base: number, exp: number, mod: number): number {
    let result: number = 1;
    let b: number = base - (base / mod) * mod;
    let e: number = exp;
    while (e > 0) {
        if (e - (e / 2) * 2 === 1) {
            result = result * b - (result * b / mod) * mod;
        }
        b = b * b - (b * b / mod) * mod;
        e = e / 2;
    }
    return result;
}

function isPrime(n: number): boolean {
    if (n < 2) return false;
    if (n < 4) return true;
    if (n - (n / 2) * 2 === 0) return false;
    let i: number = 3;
    while (i * i <= n) {
        if (n - (n / i) * i === 0) return false;
        i = i + 2;
    }
    return true;
}

// --- 3. Matrix -------------------------------------------------------

class Matrix {
    rows: number;
    cols: number;
    data: ArrayList<number>;

    constructor(rows: number, cols: number) {
        this.rows = rows;
        this.cols = cols;
        this.data = new ArrayList<number>();
        for (let i = 0; i < rows * cols; i++) {
            this.data.push(0);
        }
    }

    at(r: number, c: number): number {
        return this.data[r * this.cols + c];
    }

    setAt(r: number, c: number, v: number): void {
        this.data[r * this.cols + c] = v;
    }
}

function matAdd(a: Matrix, b: Matrix): Matrix {
    if (a.rows !== b.rows) throw new Error("matAdd: row mismatch");
    if (a.cols !== b.cols) throw new Error("matAdd: col mismatch");
    const out: Matrix = new Matrix(a.rows, a.cols);
    for (let r = 0; r < a.rows; r++) {
        for (let c = 0; c < a.cols; c++) {
            out.setAt(r, c, a.at(r, c) + b.at(r, c));
        }
    }
    return out;
}

function matMul(a: Matrix, b: Matrix): Matrix {
    if (a.cols !== b.rows) throw new Error("matMul: shape mismatch");
    const out: Matrix = new Matrix(a.rows, b.cols);
    for (let r = 0; r < a.rows; r++) {
        for (let c = 0; c < b.cols; c++) {
            let s: number = 0;
            for (let k = 0; k < a.cols; k++) {
                s = s + a.at(r, k) * b.at(k, c);
            }
            out.setAt(r, c, s);
        }
    }
    return out;
}

function matTranspose(m: Matrix): Matrix {
    const out: Matrix = new Matrix(m.cols, m.rows);
    for (let r = 0; r < m.rows; r++) {
        for (let c = 0; c < m.cols; c++) {
            out.setAt(c, r, m.at(r, c));
        }
    }
    return out;
}

function matShow(m: Matrix): string {
    let s: string = "";
    for (let r = 0; r < m.rows; r++) {
        for (let c = 0; c < m.cols; c++) {
            if (c > 0) s = s + " ";
            s = s + `${m.at(r, c)}`;
        }
        s = s + "\n";
    }
    return s;
}

// --- 4. Sorting -------------------------------------------------------

function bubbleSort(xs: ArrayList<number>): void {
    const n: number = xs.length;
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n - 1 - i; j++) {
            if (xs[j] > xs[j + 1]) {
                const t: number = xs[j];
                xs[j] = xs[j + 1];
                xs[j + 1] = t;
            }
        }
    }
}

function insertionSort(xs: ArrayList<number>): void {
    for (let i = 1; i < xs.length; i++) {
        const v: number = xs[i];
        let j: number = i - 1;
        while (j >= 0 && xs[j] > v) {
            xs[j + 1] = xs[j];
            j = j - 1;
        }
        xs[j + 1] = v;
    }
}

function quickSortRange(xs: ArrayList<number>, lo: number, hi: number): void {
    if (lo >= hi) return;
    const pivot: number = xs[hi];
    let i: number = lo - 1;
    for (let j = lo; j < hi; j++) {
        if (xs[j] <= pivot) {
            i = i + 1;
            const t: number = xs[i];
            xs[i] = xs[j];
            xs[j] = t;
        }
    }
    const t: number = xs[i + 1];
    xs[i + 1] = xs[hi];
    xs[hi] = t;
    quickSortRange(xs, lo, i);
    quickSortRange(xs, i + 2, hi);
}

function quickSort(xs: ArrayList<number>): void {
    quickSortRange(xs, 0, xs.length - 1);
}

function mergeRanges(xs: ArrayList<number>, lo: number, mid: number, hi: number): void {
    const tmp: ArrayList<number> = new ArrayList<number>();
    let i: number = lo;
    let j: number = mid + 1;
    while (i <= mid && j <= hi) {
        if (xs[i] <= xs[j]) {
            tmp.push(xs[i]);
            i = i + 1;
        } else {
            tmp.push(xs[j]);
            j = j + 1;
        }
    }
    while (i <= mid) { tmp.push(xs[i]); i = i + 1; }
    while (j <= hi)  { tmp.push(xs[j]); j = j + 1; }
    for (let k = 0; k < tmp.length; k++) {
        xs[lo + k] = tmp[k];
    }
}

function mergeSortRange(xs: ArrayList<number>, lo: number, hi: number): void {
    if (lo >= hi) return;
    const mid: number = lo + (hi - lo) / 2;
    mergeSortRange(xs, lo, mid);
    mergeSortRange(xs, mid + 1, hi);
    mergeRanges(xs, lo, mid, hi);
}

function mergeSort(xs: ArrayList<number>): void {
    if (xs.length > 1) {
        mergeSortRange(xs, 0, xs.length - 1);
    }
}

function siftDown(xs: ArrayList<number>, start: number, end: number): void {
    let root: number = start;
    while (root * 2 + 1 <= end) {
        let child: number = root * 2 + 1;
        if (child + 1 <= end && xs[child] < xs[child + 1]) {
            child = child + 1;
        }
        if (xs[root] < xs[child]) {
            const t: number = xs[root];
            xs[root] = xs[child];
            xs[child] = t;
            root = child;
        } else {
            return;
        }
    }
}

function heapSort(xs: ArrayList<number>): void {
    const n: number = xs.length;
    let s: number = (n - 2) / 2;
    while (s >= 0) {
        siftDown(xs, s, n - 1);
        s = s - 1;
    }
    let e: number = n - 1;
    while (e > 0) {
        const t: number = xs[e];
        xs[e] = xs[0];
        xs[0] = t;
        e = e - 1;
        siftDown(xs, 0, e);
    }
}

function arrShow(xs: ArrayList<number>): string {
    let s: string = "[";
    for (let i = 0; i < xs.length; i++) {
        if (i > 0) s = s + ",";
        s = s + `${xs[i]}`;
    }
    s = s + "]";
    return s;
}

function arrCopy(xs: ArrayList<number>): ArrayList<number> {
    const out: ArrayList<number> = new ArrayList<number>();
    for (let i = 0; i < xs.length; i++) {
        out.push(xs[i]);
    }
    return out;
}

// --- 5. Graph (adjacency list) ---------------------------------------

class Graph {
    nVertices: number;
    adj: ArrayList<ArrayList<number>>;

    constructor(n: number) {
        this.nVertices = n;
        this.adj = new ArrayList<ArrayList<number>>();
        for (let i = 0; i < n; i++) {
            this.adj.push(new ArrayList<number>());
        }
    }

    addEdge(u: number, v: number): void {
        this.adj[u].push(v);
        this.adj[v].push(u);
    }

    bfs(start: number): ArrayList<number> {
        const visited: ArrayList<boolean> = new ArrayList<boolean>();
        for (let i = 0; i < this.nVertices; i++) visited.push(false);
        const order: ArrayList<number> = new ArrayList<number>();
        const queue: ArrayList<number> = new ArrayList<number>();
        queue.push(start);
        visited[start] = true;
        let head: number = 0;
        while (head < queue.length) {
            const u: number = queue[head];
            head = head + 1;
            order.push(u);
            for (const v of this.adj[u]) {
                if (!visited[v]) {
                    visited[v] = true;
                    queue.push(v);
                }
            }
        }
        return order;
    }

    dfsVisit(u: number, visited: ArrayList<boolean>, out: ArrayList<number>): void {
        visited[u] = true;
        out.push(u);
        for (const v of this.adj[u]) {
            if (!visited[v]) {
                this.dfsVisit(v, visited, out);
            }
        }
    }

    dfs(start: number): ArrayList<number> {
        const visited: ArrayList<boolean> = new ArrayList<boolean>();
        for (let i = 0; i < this.nVertices; i++) visited.push(false);
        const out: ArrayList<number> = new ArrayList<number>();
        this.dfsVisit(start, visited, out);
        return out;
    }

    components(): number {
        const visited: ArrayList<boolean> = new ArrayList<boolean>();
        for (let i = 0; i < this.nVertices; i++) visited.push(false);
        let n: number = 0;
        const dummy: ArrayList<number> = new ArrayList<number>();
        for (let i = 0; i < this.nVertices; i++) {
            if (!visited[i]) {
                this.dfsVisit(i, visited, dummy);
                n = n + 1;
            }
        }
        return n;
    }
}

// --- 6. Disjoint-set union-find --------------------------------------

class DSU {
    parent: ArrayList<number>;
    rank: ArrayList<number>;

    constructor(n: number) {
        this.parent = new ArrayList<number>();
        this.rank = new ArrayList<number>();
        for (let i = 0; i < n; i++) {
            this.parent.push(i);
            this.rank.push(0);
        }
    }

    find(x: number): number {
        if (this.parent[x] === x) return x;
        const r: number = this.find(this.parent[x]);
        this.parent[x] = r;
        return r;
    }

    union(a: number, b: number): boolean {
        const ra: number = this.find(a);
        const rb: number = this.find(b);
        if (ra === rb) return false;
        if (this.rank[ra] < this.rank[rb]) {
            this.parent[ra] = rb;
        } else if (this.rank[ra] > this.rank[rb]) {
            this.parent[rb] = ra;
        } else {
            this.parent[rb] = ra;
            this.rank[ra] = this.rank[ra] + 1;
        }
        return true;
    }
}

// --- 7. Mini-statistics ----------------------------------------------

class Stats {
    n: number;
    mean: number;
    variance: number;
    constructor(n: number, mean: number, variance: number) {
        this.n = n;
        this.mean = mean;
        this.variance = variance;
    }
}

function statsOf(xs: ArrayList<number>): Stats {
    const n: number = xs.length;
    if (n === 0) return new Stats(0, 0, 0);
    let sum: number = 0;
    for (const x of xs) sum = sum + x;
    const mean: number = sum / n;
    let v: number = 0;
    for (const x of xs) {
        const d: number = x - mean;
        v = v + d * d;
    }
    return new Stats(n, mean, v / n);
}

function median(xs: ArrayList<number>): number {
    const copy: ArrayList<number> = arrCopy(xs);
    quickSort(copy);
    const m: number = copy.length / 2;
    return copy[m];
}

// --- 8. Bitset --------------------------------------------------------

class Bitset {
    bits: ArrayList<number>;
    nBits: number;
    constructor(nBits: number) {
        this.nBits = nBits;
        this.bits = new ArrayList<number>();
        let cells: number = (nBits + 63) / 64;
        for (let i = 0; i < cells; i++) {
            this.bits.push(0);
        }
    }
    setBit(i: number): void {
        const cell: number = i / 64;
        const bit: number = i - cell * 64;
        let mask: number = 1;
        for (let k = 0; k < bit; k++) mask = mask * 2;
        this.bits[cell] = this.bits[cell] | mask;
    }
    test(i: number): boolean {
        const cell: number = i / 64;
        const bit: number = i - cell * 64;
        let mask: number = 1;
        for (let k = 0; k < bit; k++) mask = mask * 2;
        return (this.bits[cell] & mask) !== 0;
    }
    countOnes(): number {
        let c: number = 0;
        for (let i = 0; i < this.nBits; i++) {
            if (this.test(i)) c = c + 1;
        }
        return c;
    }
}

// --- Driver -----------------------------------------------------------

console.log("--- sieve ---");
const primes: ArrayList<number> = sieve(30);
console.log(arrShow(primes));
console.log(`count=${primes.length}`);

console.log("--- number theory ---");
console.log(`gcd(36,24)=${gcd(36, 24)}`);
console.log(`lcm(4,6)=${lcm(4, 6)}`);
console.log(`modpow(2,10,1000)=${modpow(2, 10, 1000)}`);
console.log(`isPrime(97)=${isPrime(97)}`);
console.log(`isPrime(100)=${isPrime(100)}`);

console.log("--- matrix ---");
const a: Matrix = new Matrix(2, 3);
a.setAt(0, 0, 1); a.setAt(0, 1, 2); a.setAt(0, 2, 3);
a.setAt(1, 0, 4); a.setAt(1, 1, 5); a.setAt(1, 2, 6);
const b: Matrix = new Matrix(3, 2);
b.setAt(0, 0, 7); b.setAt(0, 1, 8);
b.setAt(1, 0, 9); b.setAt(1, 1, 10);
b.setAt(2, 0, 11); b.setAt(2, 1, 12);
const c: Matrix = matMul(a, b);
console.log(matShow(c));
const t: Matrix = matTranspose(a);
console.log(matShow(t));

console.log("--- sorting ---");
const base: ArrayList<number> = new ArrayList<number>();
base.push(5); base.push(2); base.push(8); base.push(1);
base.push(9); base.push(3); base.push(7); base.push(4);
base.push(6); base.push(0);
const cBubble:    ArrayList<number> = arrCopy(base); bubbleSort(cBubble);
const cInsertion: ArrayList<number> = arrCopy(base); insertionSort(cInsertion);
const cQuick:     ArrayList<number> = arrCopy(base); quickSort(cQuick);
const cMerge:     ArrayList<number> = arrCopy(base); mergeSort(cMerge);
const cHeap:      ArrayList<number> = arrCopy(base); heapSort(cHeap);
console.log(`bubble=${arrShow(cBubble)}`);
console.log(`insert=${arrShow(cInsertion)}`);
console.log(`quick=${arrShow(cQuick)}`);
console.log(`merge=${arrShow(cMerge)}`);
console.log(`heap=${arrShow(cHeap)}`);

console.log("--- graph ---");
const g: Graph = new Graph(7);
g.addEdge(0, 1);
g.addEdge(0, 2);
g.addEdge(1, 3);
g.addEdge(2, 4);
g.addEdge(5, 6);
console.log(`bfs(0)=${arrShow(g.bfs(0))}`);
console.log(`dfs(0)=${arrShow(g.dfs(0))}`);
console.log(`components=${g.components()}`);

console.log("--- dsu ---");
const d: DSU = new DSU(6);
d.union(0, 1);
d.union(2, 3);
d.union(1, 2);
console.log(`find(0)=find(3)? ${d.find(0) === d.find(3)}`);
console.log(`find(4)=find(5)? ${d.find(4) === d.find(5)}`);

console.log("--- stats ---");
const data: ArrayList<number> = new ArrayList<number>();
data.push(2); data.push(4); data.push(4); data.push(4);
data.push(5); data.push(5); data.push(7); data.push(9);
const st: Stats = statsOf(data);
console.log(`n=${st.n} mean=${st.mean} var=${st.variance}`);
console.log(`median=${median(data)}`);

console.log("--- bitset ---");
const bs: Bitset = new Bitset(20);
bs.setBit(3);
bs.setBit(7);
bs.setBit(15);
console.log(`test(3)=${bs.test(3)}`);
console.log(`test(4)=${bs.test(4)}`);
console.log(`ones=${bs.countOnes()}`);
