// Medium #1 (iter9): split expenses between participants
class Expense {
    let payer: String
    let amount: Int
    init(_ payer: String, _ amount: Int) {
        self.payer = payer
        self.amount = amount
    }
}

func balances(_ people: [String], _ expenses: [Expense]) -> [String: Int] {
    var total = 0
    var paid: [String: Int] = [:]
    for p in people { paid[p] = 0 }
    for e in expenses {
        total += e.amount
        paid[e.payer] = (paid[e.payer] ?? 0) + e.amount
    }
    let share = total / people.count
    var out: [String: Int] = [:]
    for p in people {
        out[p] = (paid[p] ?? 0) - share
    }
    return out
}

let people = ["alice", "bob", "carol"]
let expenses = [Expense("alice", 90), Expense("bob", 30), Expense("carol", 60), Expense("alice", 15)]
let b = balances(people, expenses)
for p in people {
    print("\(p)=\(b[p] ?? 0)")
}
