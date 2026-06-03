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
