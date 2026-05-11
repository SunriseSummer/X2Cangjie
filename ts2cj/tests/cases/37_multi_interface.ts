// 37 — Multiple interfaces (Cangjie: <: I1 & I2)
interface Named {
    getName(): string;
}

interface Counted {
    getCount(): number;
}

class Item implements Named, Counted {
    name: string;
    count: number;
    constructor(n: string, c: number) {
        this.name = n;
        this.count = c;
    }
    getName(): string {
        return this.name;
    }
    getCount(): number {
        return this.count;
    }
}

function summarize(n: Named, c: Counted): string {
    return n.getName() + " x" + c.getCount();
}

const it = new Item("apple", 7);
console.log(summarize(it, it));
