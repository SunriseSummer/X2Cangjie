// Complex class hierarchy: bank account system
open class Account(val id: String, var balance: Int) {
    open fun deposit(amount: Int) {
        balance += amount
    }

    open fun withdraw(amount: Int): Boolean {
        if (amount > balance) return false
        balance -= amount
        return true
    }

    override fun toString(): String {
        return "$id: $balance"
    }
}

class SavingsAccount(id: String, balance: Int, val interestRate: Int) : Account(id, balance) {
    fun applyInterest() {
        balance += balance * interestRate / 100
    }
}

class CheckingAccount(id: String, balance: Int, val overdraftLimit: Int) : Account(id, balance) {
    override fun withdraw(amount: Int): Boolean {
        if (amount > balance + overdraftLimit) return false
        balance -= amount
        return true
    }
}

fun transfer(from: Account, to: Account, amount: Int): Boolean {
    if (from.withdraw(amount)) {
        to.deposit(amount)
        return true
    }
    return false
}

fun main() {
    val savings = SavingsAccount("SAV001", 1000, 5)
    val checking = CheckingAccount("CHK001", 500, 200)

    println(savings)
    println(checking)

    // Deposit and withdraw
    savings.deposit(500)
    println("After deposit: $savings")
    savings.applyInterest()
    println("After interest: $savings")

    // Overdraft
    println("Withdraw 600 from checking: ${checking.withdraw(600)}")
    println(checking)
    println("Withdraw 200 from checking: ${checking.withdraw(200)}")
    println(checking)

    // Transfer
    val a1 = Account("A1", 300)
    val a2 = Account("A2", 100)
    println("Transfer 200: ${transfer(a1, a2, 200)}")
    println(a1)
    println(a2)
    println("Transfer 200: ${transfer(a1, a2, 200)}")
    println(a1)
    println(a2)
}
