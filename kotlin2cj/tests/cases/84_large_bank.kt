// ~500 line program: a tiny bank + inventory + text-processing simulation.

enum class TxnKind { DEPOSIT, WITHDRAW, TRANSFER }

data class Txn(val kind: TxnKind, val amount: Int, val note: String)

class Account(val id: Int, val owner: String) {
    var balance = 0
    val history = ArrayList<Txn>()

    fun deposit(amount: Int, note: String) {
        balance = balance + amount
        history.add(Txn(TxnKind.DEPOSIT, amount, note))
    }

    fun withdraw(amount: Int, note: String): Boolean {
        if (amount > balance) {
            return false
        }
        balance = balance - amount
        history.add(Txn(TxnKind.WITHDRAW, amount, note))
        return true
    }

    fun txnCount(): Int {
        return history.size
    }

    fun totalDeposited(): Int {
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
    val accounts = ArrayList<Account>()
    var nextId = 1

    fun open(owner: String): Account {
        val a = Account(nextId, owner)
        accounts.add(a)
        nextId = nextId + 1
        return a
    }

    fun find(id: Int): Account? {
        for (a in accounts) {
            if (a.id == id) {
                return a
            }
        }
        return null
    }

    fun transfer(fromId: Int, toId: Int, amount: Int): Boolean {
        val from = find(fromId)
        if (from != null) {
            val to = find(toId)
            if (to != null) {
                if (!from.withdraw(amount, "to " + toId)) {
                    return false
                }
                to.deposit(amount, "from " + fromId)
                return true
            }
        }
        return false
    }

    fun totalAssets(): Int {
        var total = 0
        for (a in accounts) {
            total = total + a.balance
        }
        return total
    }

    fun richest(): String {
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

fun kindName(k: TxnKind): String = when (k) {
    TxnKind.DEPOSIT -> "DEP"
    TxnKind.WITHDRAW -> "WD"
    TxnKind.TRANSFER -> "TR"
}

fun classifyAmount(amount: Int): String = when (amount) {
    in 0..99 -> "small"
    in 100..999 -> "medium"
    in 1000..9999 -> "large"
    else -> "huge"
}

data class Item(val name: String, val price: Int, val stock: Int)

class Inventory {
    val items = ArrayList<Item>()

    fun add(name: String, price: Int, stock: Int) {
        items.add(Item(name, price, stock))
    }

    fun totalValue(): Int {
        var total = 0
        for (it in items) {
            total = total + it.price * it.stock
        }
        return total
    }

    fun lowStock(threshold: Int): List<String> {
        val out = ArrayList<String>()
        for (it in items) {
            if (it.stock < threshold) {
                out.add(it.name)
            }
        }
        return out
    }

    fun priceOf(name: String): Int {
        for (it in items) {
            if (it.name == name) {
                return it.price
            }
        }
        return -1
    }
}

fun wordCount(text: String): HashMap<String, Int> {
    val counts = HashMap<String, Int>()
    val words = text.split(" ")
    for (w in words) {
        if (w.isNotEmpty()) {
            counts[w] = (counts[w] ?: 0) + 1
        }
    }
    return counts
}

fun reverseWords(text: String): String {
    val words = text.split(" ")
    val out = ArrayList<String>()
    var i = words.size - 1
    while (i >= 0) {
        out.add(words[i])
        i = i - 1
    }
    return out.joinToString(" ")
}

fun countVowels(text: String): Int {
    var n = 0
    for (c in text) {
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
            n = n + 1
        }
    }
    return n
}

fun fib(n: Int): Int {
    if (n < 2) {
        return n
    }
    var a = 0
    var b = 1
    var i = 2
    while (i <= n) {
        val c = a + b
        a = b
        b = c
        i = i + 1
    }
    return b
}

fun gcd(a: Int, b: Int): Int {
    var x = a
    var y = b
    while (y != 0) {
        val t = y
        y = x % y
        x = t
    }
    return x
}

fun isPrime(n: Int): Boolean {
    if (n < 2) {
        return false
    }
    var d = 2
    while (d * d <= n) {
        if (n % d == 0) {
            return false
        }
        d = d + 1
    }
    return true
}

fun primesUpTo(limit: Int): List<Int> {
    val out = ArrayList<Int>()
    var n = 2
    while (n <= limit) {
        if (isPrime(n)) {
            out.add(n)
        }
        n = n + 1
    }
    return out
}

fun main() {
    val bank = Bank()
    val alice = bank.open("Alice")
    val bob = bank.open("Bob")
    val carol = bank.open("Carol")

    alice.deposit(500, "salary")
    alice.deposit(150, "gift")
    bob.deposit(1200, "salary")
    carol.deposit(80, "allowance")

    println("Opened " + bank.accounts.size + " accounts")
    println("Alice balance: " + alice.balance)
    println("Bob balance: " + bob.balance)

    val ok = bank.transfer(bob.id, alice.id, 300)
    println("Transfer ok=" + ok)
    println("Alice balance: " + alice.balance)
    println("Bob balance: " + bob.balance)

    val bad = bank.transfer(carol.id, alice.id, 1000)
    println("Overdraw ok=" + bad)

    println("Total assets: " + bank.totalAssets())
    println("Richest: " + bank.richest())

    for (a in bank.accounts) {
        println(a.owner + " txns=" + a.txnCount() + " deposited=" + a.totalDeposited())
        for (t in a.history) {
            println("  " + kindName(t.kind) + " " + t.amount + " [" + classifyAmount(t.amount) + "] " + t.note)
        }
    }

    val inv = Inventory()
    inv.add("apple", 3, 40)
    inv.add("bread", 5, 8)
    inv.add("milk", 4, 3)
    inv.add("eggs", 6, 25)

    println("Inventory value: " + inv.totalValue())
    println("Low stock: " + inv.lowStock(10).joinToString(", "))
    println("Price of milk: " + inv.priceOf("milk"))

    val text = "the quick brown fox the lazy dog the fox"
    val wc = wordCount(text)
    val keys = ArrayList<String>()
    for (k in wc.keys) {
        keys.add(k)
    }
    keys.sort()
    for (k in keys) {
        println(k + ": " + wc[k])
    }
    println("Reversed: " + reverseWords(text))
    println("Vowels: " + countVowels(text))

    val fibs = ArrayList<Int>()
    var i = 0
    while (i < 12) {
        fibs.add(fib(i))
        i = i + 1
    }
    println("Fib: " + fibs.joinToString(" "))
    println("gcd(48,36)=" + gcd(48, 36))
    println("Primes<=30: " + primesUpTo(30).joinToString(" "))

    val nums = listOf(8, 3, 5, 1, 9, 2, 7, 4, 6)
    val sorted = ArrayList<Int>()
    for (n in nums) {
        sorted.add(n)
    }
    sorted.sort()
    println("Sorted: " + sorted.joinToString(" "))
    var sum = 0
    for (n in nums) {
        sum = sum + n
    }
    println("Sum: " + sum + " Avg: " + (sum / nums.size))
}
