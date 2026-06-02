package proj_inventory

import std.collection.*
import std.deriving.*

@Derive[Equatable]

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
