class Account(val id: Int, val owner: String, var balance: Double) {
    fun deposit(amount: Double) {
        if (amount > 0) {
            balance += amount
            println("  Deposited $amount to ${owner}'s account")
        }
    }

    fun withdraw(amount: Double): Boolean {
        if (amount > 0 && amount <= balance) {
            balance -= amount
            println("  Withdrew $amount from ${owner}'s account")
            return true
        }
        println("  Withdrawal of $amount failed for ${owner}")
        return false
    }

    fun info(): String {
        return "Account(id=$id, owner=$owner, balance=$balance)"
    }
}
