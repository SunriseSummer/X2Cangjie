enum class Category { FOOD, BOOK, TOY, TOOL }

data class Item(val name: String, val category: Category, val price: Int, val qty: Int)

class Store(val name: String) {
    val items = ArrayList<Item>()

    fun add(item: Item) {
        items.add(item)
    }

    fun totalValue(): Int {
        var sum = 0
        for (it in items) {
            sum += it.price * it.qty
        }
        return sum
    }

    fun countIn(cat: Category): Int {
        return items.filter { it.category == cat }.count()
    }

    fun mostExpensive(): Item {
        var best = items[0]
        for (it in items) {
            if (it.price > best.price) {
                best = it
            }
        }
        return best
    }
}

fun label(cat: Category): String = when (cat) {
    Category.FOOD -> "Food"
    Category.BOOK -> "Book"
    Category.TOY -> "Toy"
    Category.TOOL -> "Tool"
}

fun main() {
    val store = Store("Corner")
    store.add(Item("Bread", Category.FOOD, 3, 20))
    store.add(Item("Novel", Category.BOOK, 12, 5))
    store.add(Item("Block", Category.TOY, 8, 10))
    store.add(Item("Hammer", Category.TOOL, 15, 4))
    store.add(Item("Apple", Category.FOOD, 1, 50))

    println("Store: ${store.name}")
    println("Items: ${store.items.count()}")
    println("Total value: ${store.totalValue()}")
    println("Food items: ${store.countIn(Category.FOOD)}")

    val top = store.mostExpensive()
    println("Top: ${top.name} (${label(top.category)}) @ ${top.price}")

    val prices = store.items.map { it.price }
    println("Max price: ${prices.maxOrNull() ?: 0}")
    println("Sum price: ${prices.sum()}")

    val cheap = store.items.filter { it.price < 10 }
    print("Cheap: ")
    for (c in cheap) print("${c.name} ")
    println()

    var grand = 0
    for (cat in listOf(Category.FOOD, Category.BOOK, Category.TOY, Category.TOOL)) {
        val n = store.countIn(cat)
        println("${label(cat)}: $n kind(s)")
        grand += n
    }
    println("Distinct entries: $grand")
}
