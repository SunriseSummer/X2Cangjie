class Account {
    let owner: String
    var balance: Int64
    init(owner: String, balance: Int64) {
        this.owner = owner
        this.balance = balance
    }
    func deposit(amount: Int64) {
        balance += amount
    }
    func withdraw(amount: Int64): Bool {
        if (amount > balance) {
            return false
        }
        balance -= amount
        return true
    }
}

main() {
    let acc = Account("alice", 100)
    acc.deposit(50)
    let ok1 = acc.withdraw(30)
    let ok2 = acc.withdraw(500)
    println("owner=${acc.owner} balance=${acc.balance}")
    println("ok1=${ok1} ok2=${ok2}")
}
