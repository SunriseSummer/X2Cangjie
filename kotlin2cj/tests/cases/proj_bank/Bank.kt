class Bank {
    val accounts = mutableListOf<Account>()
    var nextId = 1

    fun createAccount(owner: String, initialBalance: Double): Account {
        val acc = Account(nextId, owner, initialBalance)
        accounts.add(acc)
        nextId++
        return acc
    }

    fun findAccount(id: Int): Account? {
        for (acc in accounts) {
            if (acc.id == id) return acc
        }
        return null
    }

    fun transfer(fromId: Int, toId: Int, amount: Double): Boolean {
        val from = findAccount(fromId)
        if (from != null) {
            val to = findAccount(toId)
            if (to != null) {
                if (from.withdraw(amount)) {
                    to.deposit(amount)
                    return true
                }
            }
        }
        return false
    }

    fun printAllAccounts() {
        for (acc in accounts) {
            println(acc.info())
        }
    }

    fun totalBalance(): Double {
        var total = 0.0
        for (acc in accounts) {
            total += acc.balance
        }
        return total
    }
}
