open class Account <: ToString {
    let id: String
    var balance: Int64
    init(id: String, balance: Int64) {
        this.id = id
        this.balance = balance
    }
    public open func deposit(amount: Int64) {
        balance += amount
    }
    public open func withdraw(amount: Int64): Bool {
        if (amount > balance) {
            return false
        }
        balance -= amount
        return true
    }
    public open override func toString(): String {
        return "${id}: ${balance}"
    }
}

class SavingsAccount <: Account {
    let interestRate: Int64
    init(id: String, balance: Int64, interestRate: Int64) {
        super(id, balance)
        this.interestRate = interestRate
    }
    func applyInterest() {
        balance += (balance * interestRate) / 100
    }
}

class CheckingAccount <: Account {
    let overdraftLimit: Int64
    init(id: String, balance: Int64, overdraftLimit: Int64) {
        super(id, balance)
        this.overdraftLimit = overdraftLimit
    }
    public override func withdraw(amount: Int64): Bool {
        if (amount > (balance + overdraftLimit)) {
            return false
        }
        balance -= amount
        return true
    }
}

func transfer(from: Account, to: Account, amount: Int64): Bool {
    if (from.withdraw(amount)) {
        to.deposit(amount)
        return true
    }
    return false
}

main() {
    let savings = SavingsAccount("SAV001", 1000, 5)
    let checking = CheckingAccount("CHK001", 500, 200)
    println(savings)
    println(checking)
    savings.deposit(500)
    println("After deposit: ${savings}")
    savings.applyInterest()
    println("After interest: ${savings}")
    println("Withdraw 600 from checking: ${checking.withdraw(600)}")
    println(checking)
    println("Withdraw 200 from checking: ${checking.withdraw(200)}")
    println(checking)
    let a1 = Account("A1", 300)
    let a2 = Account("A2", 100)
    println("Transfer 200: ${transfer(a1, a2, 200)}")
    println(a1)
    println(a2)
    println("Transfer 200: ${transfer(a1, a2, 200)}")
    println(a1)
    println(a2)
}
