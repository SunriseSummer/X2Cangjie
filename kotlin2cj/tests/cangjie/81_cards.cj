import std.collection.*
import std.deriving.*
import std.sort.*

@Derive[Equatable]
enum Suit <: ToString {
    | HEARTS | DIAMONDS | CLUBS | SPADES
    public func toString(): String {
    return match (this) {
                case HEARTS => "HEARTS"
            case DIAMONDS => "DIAMONDS"
            case CLUBS => "CLUBS"
            case SPADES => "SPADES"
}
    }
}

class Card <: ToString {
    let rank: Int64
    let suit: Suit
    init(rank: Int64, suit: Suit) {
        this.rank = rank
        this.suit = suit
    }
    func score(): Int64 {
        return if (rank > 10) {
            10
        } else {
            rank
        }
    }
    public func toString(): String {
        return "Card(rank=${this.rank}, suit=${this.suit})"
    }
}

class Deck {
    let cards = ArrayList<Card>()
    func add(c: Card) {
        cards.add(c)
    }
    func total(): Int64 {
        return collectArrayList(cards.iterator().map({ it => it.score() })).iterator().fold<Int64>(0, {acc, x => acc + x})
    }
    func count(): Int64 {
        return cards.size
    }
    func bySuit(s: Suit): ArrayList<Card> {
        return collectArrayList(cards.iterator().filter({ it => it.suit == s }))
    }
}

func describe(n: Int64): String {
    return if (n < 0) {
        "neg"
    } else if (n == 0) {
        "zero"
    } else if (n < 10) {
        "small"
    } else {
        "big"
    }
}

func fib(n: Int64): Int64 {
    if (n < 2) {
        return n
    }
    var a = 0
    var b = 1
    for (i in 2..=n) {
        let c = a + b
        a = b
        b = c
    }
    return b
}

main() {
    let deck = Deck()
    for (r in 1..=13) {
        for (s in ArrayList([Suit.HEARTS, Suit.SPADES])) {
            deck.add(Card(r, s))
        }
    }
    println("cards=${deck.count()}")
    println("total=${deck.total()}")
    println("hearts=${deck.bySuit(Suit.HEARTS).size}")
    let nums = ArrayList([5, -3, 0, 42, 7])
    for (n in nums) {
        println("${n} -> ${describe(n)}")
    }
    println("sum=${nums.iterator().fold<Int64>(0, {acc, x => acc + x})} max=${nums.iterator().reduce({a, b => if (a > b) { a } else { b }}).getOrThrow()} min=${nums.iterator().reduce({a, b => if (a < b) { a } else { b }}).getOrThrow()}")
    let fibs = collectArrayList((0..=10).iterator().map({ it => fib(it) }))
    println("fibs=${String.join(collectArray<String>(fibs.iterator().map({e => e.toString()})), delimiter: ",")}")
    let words = ArrayList(["apple", "banana", "cherry", "date"])
    let byLen = ({ => let _s = collectArrayList(words.iterator()); sort(_s, key: { it => it.size }, stable: true); _s })()
    println("byLen=${String.join(collectArray<String>(byLen.iterator().map({e => e.toString()})), delimiter: " ")}")
    let long = collectArrayList(words.iterator().filter({ it => it.size > 4 }))
    println("long=${String.join(collectArray<String>(long.iterator().map({e => e.toString()})), delimiter: ",")}")
    let freq = HashMap<Rune, Int64>()
    for (c in "mississippi".runes()) {
        freq[c] = (freq.get(c) ?? 0) + 1
    }
    println("s=${freq[r's']} i=${freq[r'i']}")
}
