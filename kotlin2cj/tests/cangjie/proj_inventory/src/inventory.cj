package proj_inventory

import std.collection.*
import std.deriving.*

class Inventory {
    let products = ArrayList<Product>()
    func addProduct(product: Product) {
        products.add(product)
    }
    func totalValue(): Float64 {
        var sum = 0.0
        for (p in products) {
            sum += p.price * Float64(p.quantity)
        }
        return sum
    }
    func countByCategory(cat: Category): Int64 {
        var count = 0
        for (p in products) {
            if (p.category == cat) {
                count += 1
            }
        }
        return count
    }
    func mostExpensive(): ?Product {
        if (products.isEmpty()) {
            return None
        }
        var best = products[0]
        for (i in 1..products.size) {
            if (products[i].price > best.price) {
                best = products[i]
            }
        }
        return best
    }
    func printInventory() {
        println("=== Inventory (${products.size} items) ===")
        for (p in products) {
            println("  ${p.name}: ${p.price} x${p.quantity} [${p.category}]")
        }
        println("  Total value: ${totalValue()}")
    }
}
