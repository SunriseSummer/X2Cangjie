package proj_bank

import std.collection.*

class Account {
    let id: Int64
    let owner: String
    var balance: Float64
    init(id: Int64, owner: String, balance: Float64) {
        this.id = id
        this.owner = owner
        this.balance = balance
    }
    func deposit(amount: Float64) {
        if (amount > Float64(0)) {
            balance += amount
            println("  Deposited ${amount} to ${owner}'s account")
        }
    }
    func withdraw(amount: Float64): Bool {
        if ((amount > Float64(0)) && (amount <= balance)) {
            balance -= amount
            println("  Withdrew ${amount} from ${owner}'s account")
            return true
        }
        println("  Withdrawal of ${amount} failed for ${owner}")
        return false
    }
    func info(): String {
        return "Account(id=${id}, owner=${owner}, balance=${balance})"
    }
}

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

main() {
    let bank = Bank()
    let alice = bank.createAccount("Alice", 1000.0)
    let bob = bank.createAccount("Bob", 500.0)
    println("Initial state:")
    bank.printAllAccounts()
    println("\nTransfer 200 from Alice to Bob:")
    bank.transfer(1, 2, 200.0)
    println("\nAfter transfer:")
    bank.printAllAccounts()
    println("\nTry withdraw 2000 from Bob:")
    bob.withdraw(2000.0)
    println("\nFinal state:")
    bank.printAllAccounts()
}