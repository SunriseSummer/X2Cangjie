package proj_bank

import std.collection.*

class Bank {
    let accounts = ArrayList<Account>()
    var nextId = 1
    func createAccount(owner: String, initialBalance: Float64): Account {
        let acc = Account(nextId, owner, initialBalance)
        accounts.add(acc)
        nextId += 1
        return acc
    }
    func findAccount(id: Int64): ?Account {
        for (acc in accounts) {
            if (acc.id == id) {
                return acc
            }
        }
        return None
    }
    func transfer(fromId: Int64, toId: Int64, amount: Float64): Bool {
        let from = findAccount(fromId)
        if (let Some(from) <- from) {
            let to = findAccount(toId)
            if (let Some(to) <- to) {
                if (from.withdraw(amount)) {
                    to.deposit(amount)
                    return true
                }
            }
        }
        return false
    }
    func printAllAccounts() {
        for (acc in accounts) {
            println(acc.info())
        }
    }
    func totalBalance(): Float64 {
        var total = 0.0
        for (acc in accounts) {
            total += acc.balance
        }
        return total
    }
}
