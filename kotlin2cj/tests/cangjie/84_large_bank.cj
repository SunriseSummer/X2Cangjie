import std.collection.*
import std.deriving.*
import std.sort.*

@Derive[Equatable]
enum TxnKind <: ToString {
    | DEPOSIT | WITHDRAW | TRANSFER
    public func toString(): String {
    return match (this) {
                case DEPOSIT => "DEPOSIT"
            case WITHDRAW => "WITHDRAW"
            case TRANSFER => "TRANSFER"
}
    }
}

class Txn <: ToString {
    let kind: TxnKind
    let amount: Int64
    let note: String
    init(kind: TxnKind, amount: Int64, note: String) {
        this.kind = kind
        this.amount = amount
        this.note = note
    }
    public func toString(): String {
        return "Txn(kind=${this.kind}, amount=${this.amount}, note=${this.note})"
    }
}

class Account {
    let id: Int64
    let owner: String
    init(id: Int64, owner: String) {
        this.id = id
        this.owner = owner
    }
    var balance = 0
    let history = ArrayList<Txn>()
    func deposit(amount: Int64, note: String) {
        balance = balance + amount
        history.add(Txn(TxnKind.DEPOSIT, amount, note))
    }
    func withdraw(amount: Int64, note: String): Bool {
        if (amount > balance) {
            return false
        }
        balance = balance - amount
        history.add(Txn(TxnKind.WITHDRAW, amount, note))
        return true
    }
    func txnCount(): Int64 {
        return history.size
    }
    func totalDeposited(): Int64 {
        var total = 0
        for (t in history) {
            if (t.kind == TxnKind.DEPOSIT) {
                total = total + t.amount
            }
        }
        return total
    }
}

class Bank {
    let accounts = ArrayList<Account>()
    var nextId = 1
    func `open`(owner: String): Account {
        let a = Account(nextId, owner)
        accounts.add(a)
        nextId = nextId + 1
        return a
    }
    func find(id: Int64): ?Account {
        for (a in accounts) {
            if (a.id == id) {
                return a
            }
        }
        return None
    }
    func transfer(fromId: Int64, toId: Int64, amount: Int64): Bool {
        let from = find(fromId)
        if (let Some(from) <- from) {
            let to = find(toId)
            if (let Some(to) <- to) {
                if (!from.withdraw(amount, "to " + toId.toString())) {
                    return false
                }
                to.deposit(amount, "from " + fromId.toString())
                return true
            }
        }
        return false
    }
    func totalAssets(): Int64 {
        var total = 0
        for (a in accounts) {
            total = total + a.balance
        }
        return total
    }
    func richest(): String {
        if (accounts.isEmpty()) {
            return "-"
        }
        var idx = 0
        var i = 0
        for (a in accounts) {
            if (a.balance > accounts[idx].balance) {
                idx = i
            }
            i = i + 1
        }
        return accounts[idx].owner
    }
}

func kindName(k: TxnKind): String {
    return match (k) {
        case TxnKind.DEPOSIT => "DEP"
        case TxnKind.WITHDRAW => "WD"
        case TxnKind.TRANSFER => "TR"}
}

func classifyAmount(amount: Int64): String {
    return if (amount >= 0 && amount <= 99) {
        "small"
    } else if (amount >= 100 && amount <= 999) {
        "medium"
    } else if (amount >= 1000 && amount <= 9999) {
        "large"
    } else {
        "huge"
    }
}

class Item <: ToString {
    let name: String
    let price: Int64
    let stock: Int64
    init(name: String, price: Int64, stock: Int64) {
        this.name = name
        this.price = price
        this.stock = stock
    }
    public func toString(): String {
        return "Item(name=${this.name}, price=${this.price}, stock=${this.stock})"
    }
}

class Inventory {
    let items = ArrayList<Item>()
    func add(name: String, price: Int64, stock: Int64) {
        items.add(Item(name, price, stock))
    }
    func totalValue(): Int64 {
        var total = 0
        for (it in items) {
            total = total + (it.price * it.stock)
        }
        return total
    }
    func lowStock(threshold: Int64): ArrayList<String> {
        let out = ArrayList<String>()
        for (it in items) {
            if (it.stock < threshold) {
                out.add(it.name)
            }
        }
        return out
    }
    func priceOf(name: String): Int64 {
        for (it in items) {
            if (it.name == name) {
                return it.price
            }
        }
        return -1
    }
}

func wordCount(text: String): HashMap<String, Int64> {
    let counts = HashMap<String, Int64>()
    let words = collectArrayList(text.split(" ").iterator())
    for (w in words) {
        if (!(w.isEmpty())) {
            counts[w] = (counts.get(w) ?? 0) + 1
        }
    }
    return counts
}

func reverseWords(text: String): String {
    let words = collectArrayList(text.split(" ").iterator())
    let out = ArrayList<String>()
    var i = words.size - 1
    while (i >= 0) {
        out.add(words[i])
        i = i - 1
    }
    return String.join(collectArray<String>(out.iterator().map({e => e.toString()})), delimiter: " ")
}

func countVowels(text: String): Int64 {
    var n = 0
    for (c in text.runes()) {
        if (((((c == r'a') || (c == r'e')) || (c == r'i')) || (c == r'o')) || (c == r'u')) {
            n = n + 1
        }
    }
    return n
}

func fib(n: Int64): Int64 {
    if (n < 2) {
        return n
    }
    var a = 0
    var b = 1
    var i = 2
    while (i <= n) {
        let c = a + b
        a = b
        b = c
        i = i + 1
    }
    return b
}

func gcd(a: Int64, b: Int64): Int64 {
    var x = a
    var y = b
    while (y != 0) {
        let t = y
        y = x % y
        x = t
    }
    return x
}

func isPrime(n: Int64): Bool {
    if (n < 2) {
        return false
    }
    var d = 2
    while ((d * d) <= n) {
        if ((n % d) == 0) {
            return false
        }
        d = d + 1
    }
    return true
}

func primesUpTo(limit: Int64): ArrayList<Int64> {
    let out = ArrayList<Int64>()
    var n = 2
    while (n <= limit) {
        if (isPrime(n)) {
            out.add(n)
        }
        n = n + 1
    }
    return out
}

main() {
    let bank = Bank()
    let alice = bank.`open`("Alice")
    let bob = bank.`open`("Bob")
    let carol = bank.`open`("Carol")
    alice.deposit(500, "salary")
    alice.deposit(150, "gift")
    bob.deposit(1200, "salary")
    carol.deposit(80, "allowance")
    println(("Opened " + bank.accounts.size.toString()) + " accounts")
    println("Alice balance: " + alice.balance.toString())
    println("Bob balance: " + bob.balance.toString())
    let ok = bank.transfer(bob.id, alice.id, 300)
    println("Transfer ok=" + ok.toString())
    println("Alice balance: " + alice.balance.toString())
    println("Bob balance: " + bob.balance.toString())
    let bad = bank.transfer(carol.id, alice.id, 1000)
    println("Overdraw ok=" + bad.toString())
    println("Total assets: " + bank.totalAssets().toString())
    println("Richest: " + bank.richest().toString())
    for (a in bank.accounts) {
        println((((a.owner.toString() + " txns=") + a.txnCount().toString()) + " deposited=") + a.totalDeposited().toString())
        for (t in a.history) {
            println((((((("  " + kindName(t.kind).toString()) + " ") + t.amount.toString()) + " [") + classifyAmount(t.amount).toString()) + "] ") + t.note.toString())
        }
    }
    let inv = Inventory()
    inv.add("apple", 3, 40)
    inv.add("bread", 5, 8)
    inv.add("milk", 4, 3)
    inv.add("eggs", 6, 25)
    println("Inventory value: " + inv.totalValue().toString())
    println("Low stock: " + String.join(collectArray<String>(inv.lowStock(10).iterator().map({e => e.toString()})), delimiter: ", "))
    println("Price of milk: " + inv.priceOf("milk").toString())
    let text = "the quick brown fox the lazy dog the fox"
    let wc = wordCount(text)
    let keys = ArrayList<String>()
    for (k in wc.keys()) {
        keys.add(k)
    }
    sort(keys, stable: true)
    for (k in keys) {
        println((k + ": ") + wc[k].toString())
    }
    println("Reversed: " + reverseWords(text).toString())
    println("Vowels: " + countVowels(text).toString())
    let fibs = ArrayList<Int64>()
    var i = 0
    while (i < 12) {
        fibs.add(fib(i))
        i = i + 1
    }
    println("Fib: " + String.join(collectArray<String>(fibs.iterator().map({e => e.toString()})), delimiter: " "))
    println("gcd(48,36)=" + gcd(48, 36).toString())
    println("Primes<=30: " + String.join(collectArray<String>(primesUpTo(30).iterator().map({e => e.toString()})), delimiter: " "))
    let nums = ArrayList([8, 3, 5, 1, 9, 2, 7, 4, 6])
    let sorted = ArrayList<Int64>()
    for (n in nums) {
        sorted.add(n)
    }
    sort(sorted, stable: true)
    println("Sorted: " + String.join(collectArray<String>(sorted.iterator().map({e => e.toString()})), delimiter: " "))
    var sum = 0
    for (n in nums) {
        sum = sum + n
    }
    println((("Sum: " + sum.toString()) + " Avg: ") + (sum / nums.size).toString())
}
