// Bank account system (~110 lines).  Demonstrates: class hierarchies,
// override, throw/try-catch, ArrayList<T>, string interpolation, multi-
// step business logic.  This is a small but realistic Cangjie program.

class InsufficientFundsError {
    msg: string;
    constructor(msg: string) {
        this.msg = msg;
    }
}

class Account {
    id: number;
    owner: string;
    balance: number;

    constructor(id: number, owner: string, opening: number) {
        this.id = id;
        this.owner = owner;
        this.balance = opening;
    }

    deposit(amount: number): void {
        this.balance = this.balance + amount;
    }

    withdraw(amount: number): void {
        if (amount > this.balance) {
            throw new Error(`acct#${this.id}: insufficient funds`);
        }
        this.balance = this.balance - amount;
    }

    describe(): string {
        return `Account#${this.id} (${this.owner}): ${this.balance}`;
    }
}

class SavingsAccount extends Account {
    rate: number;
    constructor(id: number, owner: string, opening: number, rate: number) {
        super(id, owner, opening);
        this.rate = rate;
    }
    accrue(): void {
        const interest: number = this.balance * this.rate / 100;
        this.deposit(interest);
    }
    describe(): string {
        return `Savings#${this.id} (${this.owner}): ${this.balance} @${this.rate}%`;
    }
}

function transfer(from: Account, to: Account, amount: number): void {
    from.withdraw(amount);
    to.deposit(amount);
}

function totalAssets(accounts: ArrayList<Account>): number {
    let sum: number = 0;
    for (const a of accounts) {
        sum = sum + a.balance;
    }
    return sum;
}

const alice: Account = new Account(1, "Alice", 1000);
const bob: Account = new Account(2, "Bob", 500);
const savings: SavingsAccount = new SavingsAccount(3, "Carol", 2000, 5);

const all: ArrayList<Account> = new ArrayList<Account>();
all.push(alice);
all.push(bob);
all.push(savings);

console.log(alice.describe());
console.log(bob.describe());
console.log(savings.describe());

transfer(alice, bob, 250);
console.log(alice.describe());
console.log(bob.describe());

savings.accrue();
console.log(savings.describe());

console.log(`total=${totalAssets(all)}`);

try {
    transfer(bob, alice, 9999);
    console.log("transfer ok (unexpected)");
} catch (e) {
    console.log("caught insufficient funds");
}
