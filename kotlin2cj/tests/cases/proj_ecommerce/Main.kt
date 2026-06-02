fun main() {
    val catalog = ProductCatalog()
    catalog.addProduct(Product("Laptop", 999, 10))
    catalog.addProduct(Product("Mouse", 25, 100))
    catalog.addProduct(Product("Keyboard", 75, 50))
    catalog.addProduct(Product("Monitor", 450, 20))
    catalog.addProduct(Product("Headset", 60, 80))

    println("Product Catalog:")
    catalog.listProducts()
    println("Total products: ${catalog.totalProducts()}")

    val alice = Customer("Alice", 1)
    val bob = Customer("Bob", 2)

    val cart1 = ShoppingCart(alice)
    val laptop = catalog.findByName("Laptop")
    if (laptop != null) {
        cart1.addItem(laptop, 1)
    }
    val mouse = catalog.findByName("Mouse")
    if (mouse != null) {
        cart1.addItem(mouse, 2)
    }

    val cart2 = ShoppingCart(bob)
    val kb = catalog.findByName("Keyboard")
    if (kb != null) {
        cart2.addItem(kb, 1)
    }
    val headset = catalog.findByName("Headset")
    if (headset != null) {
        cart2.addItem(headset, 1)
    }

    println()
    cart1.printCart()
    println()
    cart2.printCart()

    println()
    val processor = OrderProcessor()
    val o1 = processor.checkout(cart1)
    val o2 = processor.checkout(cart2)
    processor.processAll()

    println()
    processor.printSummary()

    println()
    println(alice.info())
    println(bob.info())
}
