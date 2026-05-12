// Large #1 (iter2): bank ledger with accounts, transactions, dispute handling (~200 lines)
enum TxKind {
    case deposit
    case withdraw
    case transferOut
    case transferIn
}

class Tx {
    let id: Int
    let kind: TxKind
    let amount: Int
    let other: Int  // counterparty for transfers, -1 otherwise
    var disputed: Bool = false

    init(id: Int, kind: TxKind, amount: Int, other: Int) {
        self.id = id
        self.kind = kind
        self.amount = amount
        self.other = other
    }

    func kindName() -> String {
        switch kind {
        case .deposit:
            return "DEP"
        case .withdraw:
            return "WD"
        case .transferOut:
            return "TX-OUT"
        case .transferIn:
            return "TX-IN"
        }
    }
}

class Account {
    let id: Int
    var balance: Int = 0
    var txs: [Tx] = []
    let owner: String

    init(id: Int, owner: String) {
        self.id = id
        self.owner = owner
    }

    func deposit(amount: Int, txId: Int) {
        balance += amount
        txs.append(Tx(id: txId, kind: .deposit, amount: amount, other: -1))
    }

    func withdraw(amount: Int, txId: Int) -> Bool {
        if balance < amount {
            return false
        }
        balance -= amount
        txs.append(Tx(id: txId, kind: .withdraw, amount: amount, other: -1))
        return true
    }

    func transferOut(amount: Int, to: Int, txId: Int) -> Bool {
        if balance < amount {
            return false
        }
        balance -= amount
        txs.append(Tx(id: txId, kind: .transferOut, amount: amount, other: to))
        return true
    }

    func transferIn(amount: Int, from: Int, txId: Int) {
        balance += amount
        txs.append(Tx(id: txId, kind: .transferIn, amount: amount, other: from))
    }

    func summary() -> String {
        return "[\(id):\(owner)] balance=\(balance) tx_count=\(txs.count)"
    }
}

class Bank {
    var accounts: [Int: Account] = [:]
    var nextTxId: Int = 1000

    func open(id: Int, owner: String) {
        accounts[id] = Account(id: id, owner: owner)
    }

    func deposit(id: Int, amount: Int) -> Int {
        let txId = nextTxId
        nextTxId += 1
        accounts[id]!.deposit(amount: amount, txId: txId)
        return txId
    }

    func withdraw(id: Int, amount: Int) -> Bool {
        let txId = nextTxId
        nextTxId += 1
        return accounts[id]!.withdraw(amount: amount, txId: txId)
    }

    func transfer(from: Int, to: Int, amount: Int) -> Bool {
        let txId = nextTxId
        nextTxId += 1
        if !accounts[from]!.transferOut(amount: amount, to: to, txId: txId) {
            return false
        }
        accounts[to]!.transferIn(amount: amount, from: from, txId: txId)
        return true
    }

    func totalAssets() -> Int {
        var s = 0
        for (_, a) in accounts {
            s += a.balance
        }
        return s
    }

    func reportAll(ids: [Int]) {
        for id in ids {
            let a = accounts[id]!
            print(a.summary())
            for t in a.txs {
                print("  \(t.kindName()) id=\(t.id) amount=\(t.amount) other=\(t.other)")
            }
        }
    }
}

let bank = Bank()
bank.open(id: 1, owner: "Alice")
bank.open(id: 2, owner: "Bob")
bank.open(id: 3, owner: "Carol")

let _ = bank.deposit(id: 1, amount: 1000)
let _ = bank.deposit(id: 2, amount: 500)
let _ = bank.deposit(id: 3, amount: 200)
print("after deposits: total=\(bank.totalAssets())")

let ok1 = bank.transfer(from: 1, to: 2, amount: 300)
print("transfer 1→2 300 = \(ok1)")
let ok2 = bank.transfer(from: 2, to: 3, amount: 1000) // should fail
print("transfer 2→3 1000 = \(ok2)")
let okW = bank.withdraw(id: 1, amount: 200)
print("withdraw a1 200 = \(okW)")
let okW2 = bank.withdraw(id: 3, amount: 999) // fail
print("withdraw a3 999 = \(okW2)")

print("final total = \(bank.totalAssets())")
let allIds = [1, 2, 3]
bank.reportAll(ids: allIds)
