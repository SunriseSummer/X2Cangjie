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

@Derive[Equatable]
enum Category <: ToString {
    | FOOD | ELECTRONICS | CLOTHING | BOOKS
    public func toString(): String {
    return match (this) {
                case FOOD => "FOOD"
            case ELECTRONICS => "ELECTRONICS"
            case CLOTHING => "CLOTHING"
            case BOOKS => "BOOKS"
}
    }
}

class Product <: ToString {
    let name: String
    let price: Float64
    let category: Category
    let quantity: Int64
    init(name: String, price: Float64, category: Category, quantity: Int64) {
        this.name = name
        this.price = price
        this.category = category
        this.quantity = quantity
    }
    public func toString(): String {
        return "Product(name=${this.name}, price=${this.price}, category=${this.category}, quantity=${this.quantity})"
    }
}

main() {
    let inv = Inventory()
    inv.addProduct(Product("Apple", 1.5, Category.FOOD, 100))
    inv.addProduct(Product("Laptop", 999.0, Category.ELECTRONICS, 5))
    inv.addProduct(Product("T-Shirt", 25.0, Category.CLOTHING, 50))
    inv.addProduct(Product("Novel", 12.0, Category.BOOKS, 30))
    inv.addProduct(Product("Bread", 3.0, Category.FOOD, 200))
    inv.printInventory()
    println("\nFood items: ${inv.countByCategory(Category.FOOD)}")
    println("Electronics items: ${inv.countByCategory(Category.ELECTRONICS)}")
    let expensive = inv.mostExpensive()
    if (let Some(expensive) <- expensive) {
        println("Most expensive: ${expensive.name} (${expensive.price})")
    }
}