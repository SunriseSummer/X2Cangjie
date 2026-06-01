enum class Suit { HEARTS, DIAMONDS, CLUBS, SPADES }

data class Card(val rank: Int, val suit: Suit) {
    fun score(): Int = if (rank > 10) 10 else rank
}

class Deck {
    val cards = ArrayList<Card>()
    fun add(c: Card) { cards.add(c) }
    fun total(): Int = cards.map { it.score() }.sum()
    fun count(): Int = cards.size
    fun bySuit(s: Suit): List<Card> = cards.filter { it.suit == s }
}

fun describe(n: Int): String = when {
    n < 0 -> "neg"
    n == 0 -> "zero"
    n < 10 -> "small"
    else -> "big"
}

fun fib(n: Int): Int {
    if (n < 2) return n
    var a = 0
    var b = 1
    for (i in 2..n) {
        val c = a + b
        a = b
        b = c
    }
    return b
}

fun main() {
    val deck = Deck()
    for (r in 1..13) {
        for (s in listOf(Suit.HEARTS, Suit.SPADES)) {
            deck.add(Card(r, s))
        }
    }
    println("cards=${deck.count()}")
    println("total=${deck.total()}")
    println("hearts=${deck.bySuit(Suit.HEARTS).size}")

    val nums = listOf(5, -3, 0, 42, 7)
    for (n in nums) println("$n -> ${describe(n)}")
    println("sum=${nums.sum()} max=${nums.max()} min=${nums.min()}")

    val fibs = (0..10).map { fib(it) }
    println("fibs=${fibs.joinToString(",")}")

    val words = listOf("apple", "banana", "cherry", "date")
    val byLen = words.sortedBy { it.length }
    println("byLen=${byLen.joinToString(" ")}")
    val long = words.filter { it.length > 4 }
    println("long=${long.joinToString(",")}")

    val freq = HashMap<Char, Int>()
    for (c in "mississippi") {
        freq[c] = (freq[c] ?: 0) + 1
    }
    println("s=${freq['s']} i=${freq['i']}")
}
