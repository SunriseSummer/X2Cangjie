enum class Category {
    FOOD, TOOL, BOOK
}

class Item(val name: String, val category: Category, var qty: Int) {
    fun restock(amount: Int) {
        qty += amount
    }
}

fun categoryName(c: Category): String {
    return when (c) {
        Category.FOOD -> "food"
        Category.TOOL -> "tool"
        else -> "book"
    }
}

fun main() {
    val items = mutableListOf<Item>()
    items.add(Item("apple", Category.FOOD, 3))
    items.add(Item("hammer", Category.TOOL, 1))
    items.add(Item("novel", Category.BOOK, 5))

    items[0].restock(7)

    var total = 0
    for (it in items) {
        total += it.qty
        println("${it.name} [${categoryName(it.category)}] x${it.qty}")
    }
    println("total=$total")

    val counts = mutableMapOf<String, Int>()
    for (it in items) {
        val key = categoryName(it.category)
        counts[key] = (counts[key] ?: 0) + it.qty
    }
    var food = counts["food"] ?: 0
    println("food count=$food")
}
