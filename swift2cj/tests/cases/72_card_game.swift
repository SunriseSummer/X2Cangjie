// Card game simulation — ~400 lines.
// Exercises: enum w/ raw, enum w/ associated values, struct + operator overload,
// class + protocol, generic class, closures, switch destructure,
// guard/ternary, ranges, arrays/dictionaries.

enum Suit: Int {
    case clubs = 0
    case diamonds = 1
    case hearts = 2
    case spades = 3
}

func suitName(_ s: Suit) -> String {
    switch s {
    case .clubs:    return "C"
    case .diamonds: return "D"
    case .hearts:   return "H"
    case .spades:   return "S"
    }
}

enum Rank: Int {
    case two = 2
    case three = 3
    case four = 4
    case five = 5
    case six = 6
    case seven = 7
    case eight = 8
    case nine = 9
    case ten = 10
    case jack = 11
    case queen = 12
    case king = 13
    case ace = 14
}

func rankValue(_ r: Rank) -> Int {
    switch r {
    case .two: return 2
    case .three: return 3
    case .four: return 4
    case .five: return 5
    case .six: return 6
    case .seven: return 7
    case .eight: return 8
    case .nine: return 9
    case .ten: return 10
    case .jack: return 11
    case .queen: return 12
    case .king: return 13
    case .ace: return 14
    }
}

func rankName(_ r: Rank) -> String {
    switch r {
    case .two: return "2"
    case .three: return "3"
    case .four: return "4"
    case .five: return "5"
    case .six: return "6"
    case .seven: return "7"
    case .eight: return "8"
    case .nine: return "9"
    case .ten: return "T"
    case .jack: return "J"
    case .queen: return "Q"
    case .king: return "K"
    case .ace: return "A"
    }
}

struct Card {
    var suit: Suit
    var rank: Rank
    func describe() -> String {
        return "\(rankName(self.rank))\(suitName(self.suit))"
    }
    func value() -> Int {
        return rankValue(self.rank)
    }
}

// Generic stack
class Stack<T> {
    var items: [T] = []
    func push(_ x: T) {
        self.items.append(x)
    }
    func size() -> Int {
        return self.items.count
    }
    func isEmpty() -> Bool {
        return self.items.count == 0
    }
}

protocol Player {
    func receive(_ c: Card)
    func hand() -> [Card]
    func name() -> String
}

class Human: Player {
    var who: String
    var cards: [Card] = []
    init(who: String) {
        self.who = who
    }
    func receive(_ c: Card) {
        self.cards.append(c)
    }
    func hand() -> [Card] {
        return self.cards
    }
    func name() -> String {
        return self.who
    }
    func score() -> Int {
        var s = 0
        for c in self.cards {
            s += c.value()
        }
        return s
    }
}

// A discrete event in the game
enum Event {
    case deal(Int)        // round
    case play(Int, Int)   // playerIdx, cardIdx
    case finish(Int)      // winnerIdx
}

func eventName(_ e: Event) -> String {
    switch e {
    case .deal(let r):
        return "deal-round-\(r)"
    case .play(let p, let c):
        return "play(p=\(p), c=\(c))"
    case .finish(let w):
        return "finish(winner=\(w))"
    }
}

// Money/score arithmetic
struct Score {
    var value: Int
    static func + (a: Score, b: Score) -> Score {
        return Score(value: a.value + b.value)
    }
    static func - (a: Score, b: Score) -> Score {
        return Score(value: a.value - b.value)
    }
    static func * (a: Score, k: Int) -> Score {
        return Score(value: a.value * k)
    }
}

// Build all 52 cards
func buildDeck() -> [Card] {
    let suits: [Suit] = [.clubs, .diamonds, .hearts, .spades]
    let ranks: [Rank] = [.two, .three, .four, .five, .six, .seven,
                         .eight, .nine, .ten, .jack, .queen, .king, .ace]
    var out: [Card] = []
    for s in suits {
        for r in ranks {
            out.append(Card(suit: s, rank: r))
        }
    }
    return out
}

// Linear-congruential generator for reproducibility
class LCG {
    var state: Int = 1
    init(seed: Int) {
        self.state = seed
    }
    func next() -> Int {
        // Avoid overflow with modular arithmetic.
        self.state = (self.state * 1103515245 + 12345) % 2147483647
        return self.state
    }
    func nextRange(_ n: Int) -> Int {
        let v = self.next()
        return v >= 0 ? v % n : -v % n
    }
}

func shuffle(_ deck: [Card], rng: LCG) -> [Card] {
    var arr: [Card] = []
    for c in deck {
        arr.append(c)
    }
    let n = arr.count
    var i = n - 1
    while i > 0 {
        let j = rng.nextRange(i + 1)
        let tmp = arr[i]
        arr[i] = arr[j]
        arr[j] = tmp
        i -= 1
    }
    return arr
}

func dealCards(_ deck: [Card], players: [Human], handSize: Int) {
    var idx = 0
    for h in 0 ..< handSize {
        for p in players {
            if idx < deck.count {
                p.receive(deck[idx])
                idx += 1
            }
        }
    }
}

// Highest-score wins
func winner(_ players: [Human]) -> Int {
    var best = 0
    var bestScore = players[0].score()
    for i in 1 ..< players.count {
        if players[i].score() > bestScore {
            bestScore = players[i].score()
            best = i
        }
    }
    return best
}

func describeHand(_ p: Human) -> String {
    var pieces: [String] = []
    for c in p.hand() {
        pieces.append(c.describe())
    }
    var result = p.name() + ": ["
    var first = true
    for piece in pieces {
        if first {
            result = result + piece
            first = false
        } else {
            result = result + " " + piece
        }
    }
    result = result + "] score=\(p.score())"
    return result
}

// --- main ---

let deck0 = buildDeck()
print("deck size =", deck0.count)
print("first =", deck0[0].describe())
print("last =", deck0[51].describe())

// Score arithmetic
let s1 = Score(value: 10)
let s2 = Score(value: 3)
let s3 = s1 + s2
let s4 = s1 - s2
let s5 = s2 * 4
print("score:", s3.value, s4.value, s5.value)

// Event names
let events: [Event] = [.deal(1), .play(0, 3), .play(1, 5), .finish(0)]
for e in events {
    print(eventName(e))
}

// Deal a game (no shuffle for deterministic output)
let deck = buildDeck()
let players: [Human] = [Human(who: "Alice"), Human(who: "Bob"), Human(who: "Carol")]
dealCards(deck, players: players, handSize: 5)
for p in players {
    print(describeHand(p))
}
let w = winner(players)
print("winner index =", w)
print("winner name =", players[w].name())

// Generic stack
let stack = Stack<Int>()
stack.push(1)
stack.push(2)
stack.push(3)
print("stack size =", stack.size())
print("stack empty =", stack.isEmpty() ? "yes" : "no")

// guard / ternary
func clamp(_ x: Int, lo: Int, hi: Int) -> Int {
    guard x >= lo else { return lo }
    return x > hi ? hi : x
}
print(clamp(-5, lo: 0, hi: 10))
print(clamp(50, lo: 0, hi: 10))
print(clamp(5, lo: 0, hi: 10))

// closures, single line
let dbl: (Int) -> Int = { x in x * 2 }
let neg: (Int) -> Int = { x in -x }
let inc: (Int) -> Int = { x in x + 1 }
print(dbl(5), neg(5), inc(5))

// switch on suit
func suitColor(_ s: Suit) -> String {
    switch s {
    case .clubs, .spades: return "black"
    case .diamonds, .hearts: return "red"
    }
}
print(suitColor(.clubs))
print(suitColor(.hearts))

// switch on rank → face? 
func isFace(_ r: Rank) -> Bool {
    switch r {
    case .jack, .queen, .king: return true
    default: return false
    }
}
print(isFace(.queen) ? "Q-face" : "Q-no")
print(isFace(.three) ? "3-face" : "3-no")

print("done")
