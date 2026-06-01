// ~500 line mixed program: simple e-commerce / orders domain.

enum class Category { BOOK, FOOD, TOY, TECH }

data class Product(val id: Int, val name: String, val price: Int, val category: Category)

data class OrderLine(val product: Product, val qty: Int)

class Order(val id: Int, val customer: String) {
    val lines = ArrayList<OrderLine>()

    fun addLine(p: Product, qty: Int) {
        lines.add(OrderLine(p, qty))
    }

    fun subtotal(): Int {
        var total = 0
        for (l in lines) {
            total = total + l.product.price * l.qty
        }
        return total
    }

    fun itemCount(): Int {
        var n = 0
        for (l in lines) {
            n = n + l.qty
        }
        return n
    }

    fun categories(): List<Category> {
        val seen = ArrayList<Category>()
        for (l in lines) {
            if (!seen.contains(l.product.category)) {
                seen.add(l.product.category)
            }
        }
        return seen
    }
}

class Catalog {
    val products = ArrayList<Product>()
    var nextId = 1

    fun add(name: String, price: Int, cat: Category): Product {
        val p = Product(nextId, name, price, cat)
        products.add(p)
        nextId = nextId + 1
        return p
    }

    fun findByCategory(cat: Category): List<Product> {
        val out = ArrayList<Product>()
        for (p in products) {
            if (p.category == cat) {
                out.add(p)
            }
        }
        return out
    }

    fun cheapest(): Product {
        var best = products[0]
        for (p in products) {
            if (p.price < best.price) {
                best = p
            }
        }
        return best
    }

    fun priciest(): Product {
        var best = products[0]
        for (p in products) {
            if (p.price > best.price) {
                best = p
            }
        }
        return best
    }
}

fun discountFor(total: Int): Int {
    return when {
        total >= 1000 -> total / 10
        total >= 500 -> total / 20
        total >= 100 -> total / 50
        else -> 0
    }
}

fun categoryLabel(c: Category): String {
    return when (c) {
        Category.BOOK -> "Books"
        Category.FOOD -> "Groceries"
        Category.TOY -> "Toys"
        Category.TECH -> "Electronics"
    }
}

fun formatMoney(cents: Int): String {
    val dollars = cents / 100
    val rem = cents % 100
    val r = if (rem < 10) "0$rem" else "$rem"
    return "\$$dollars.$r"
}

class Report {
    val counters = HashMap<String, Int>()

    fun record(key: String, amount: Int) {
        counters[key] = counters.getOrDefault(key, 0) + amount
    }

    fun dump() {
        val keys = ArrayList<String>()
        for (k in counters.keys) {
            keys.add(k)
        }
        keys.sort()
        for (k in keys) {
            println("  $k: ${counters[k]}")
        }
    }
}

fun main() {
    val catalog = Catalog()
    catalog.add("Kotlin in Action", 4500, Category.BOOK)
    catalog.add("Apple", 50, Category.FOOD)
    catalog.add("Lego Set", 8000, Category.TOY)
    catalog.add("Headphones", 12000, Category.TECH)
    catalog.add("Cookbook", 3000, Category.BOOK)
    catalog.add("Bread", 250, Category.FOOD)
    catalog.add("Puzzle", 1500, Category.TOY)
    catalog.add("Mouse", 2500, Category.TECH)

    println("=== Catalog ===")
    for (p in catalog.products) {
        println("${p.id}. ${p.name} [${categoryLabel(p.category)}] ${formatMoney(p.price)}")
    }

    println("Cheapest: ${catalog.cheapest().name}")
    println("Priciest: ${catalog.priciest().name}")

    println("=== Books ===")
    val books = catalog.findByCategory(Category.BOOK)
    for (b in books) {
        println("- ${b.name}")
    }

    val orders = ArrayList<Order>()
    val o1 = Order(1, "Alice")
    o1.addLine(catalog.products[0], 1)
    o1.addLine(catalog.products[3], 2)
    orders.add(o1)

    val o2 = Order(2, "Bob")
    o2.addLine(catalog.products[1], 10)
    o2.addLine(catalog.products[5], 3)
    o2.addLine(catalog.products[6], 1)
    orders.add(o2)

    val o3 = Order(3, "Carol")
    o3.addLine(catalog.products[2], 1)
    o3.addLine(catalog.products[7], 2)
    o3.addLine(catalog.products[4], 1)
    orders.add(o3)

    val report = Report()
    var grandTotal = 0
    println("=== Orders ===")
    for (o in orders) {
        val sub = o.subtotal()
        val disc = discountFor(sub)
        val net = sub - disc
        grandTotal = grandTotal + net
        println("Order #${o.id} (${o.customer}): items=${o.itemCount()} sub=${formatMoney(sub)} disc=${formatMoney(disc)} net=${formatMoney(net)}")
        for (c in o.categories()) {
            report.record(categoryLabel(c), 1)
        }
        report.record("revenue", net)
    }

    println("=== Report ===")
    report.dump()
    println("Grand total: ${formatMoney(grandTotal)}")

    // functional aggregation
    val allPrices = ArrayList<Int>()
    for (p in catalog.products) {
        allPrices.add(p.price)
    }
    val sumPrices = allPrices.sum()
    val avgPrice = sumPrices / allPrices.size
    println("Avg catalog price: ${formatMoney(avgPrice)}")

    val expensive = allPrices.filter { it > 2000 }
    println("Expensive count: ${expensive.size}")

    val doubled = allPrices.map { it * 2 }
    var dsum = 0
    for (d in doubled) {
        dsum = dsum + d
    }
    println("Doubled sum: $dsum")

    val sorted = allPrices.sorted()
    println("Sorted prices: $sorted")
    println("Min: ${sorted.first()} Max: ${sorted.last()}")
}
