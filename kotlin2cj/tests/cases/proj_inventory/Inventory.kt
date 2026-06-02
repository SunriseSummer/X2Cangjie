class Inventory {
    val products = mutableListOf<Product>()

    fun addProduct(product: Product) {
        products.add(product)
    }

    fun totalValue(): Double {
        var sum = 0.0
        for (p in products) {
            sum += p.price * p.quantity
        }
        return sum
    }

    fun countByCategory(cat: Category): Int {
        var count = 0
        for (p in products) {
            if (p.category == cat) {
                count++
            }
        }
        return count
    }

    fun mostExpensive(): Product? {
        if (products.isEmpty()) return null
        var best = products[0]
        for (i in 1 until products.size) {
            if (products[i].price > best.price) {
                best = products[i]
            }
        }
        return best
    }

    fun printInventory() {
        println("=== Inventory (${products.size} items) ===")
        for (p in products) {
            println("  ${p.name}: ${p.price} x${p.quantity} [${p.category}]")
        }
        println("  Total value: ${totalValue()}")
    }
}
