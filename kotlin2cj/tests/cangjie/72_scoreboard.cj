import std.collection.*

class Player <: ToString {
    let name: String
    let score: Int64
    init(name: String, score: Int64) {
        this.name = name
        this.score = score
    }
    public func toString(): String {
        return "Player(name=${this.name}, score=${this.score})"
    }
}

main() {
    let players = ArrayList([Player("Alice", 88), Player("Bob", 72), Player("Carol", 95), Player("Dave", 60), Player("Eve", 81)])
    let total = players.iterator().map({ it => it.score }).fold<Int64>(0, {acc, x => acc + x})
    let avg = total / players.size
    println("total=${total} avg=${avg}")
    let passed = collectArrayList(players.iterator().filter({ it => it.score >= 80 }))
    print("passed: ")
    for (p in passed) {
        print("${p.name} ")
    }
    println()
    println("topScore=${collectArrayList(players.iterator().map({ it => it.score })).iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0}")
    println("allPass=${players.iterator().all({ it => it.score >= 50 })} anyPerfect=${players.iterator().any({ it => it.score == 100 })}")
    let names = String.join(collectArray<String>(players.iterator().map({ it => it.name })), delimiter: ", ")
    println("roster: ${names}")
}
