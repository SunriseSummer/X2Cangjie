package proj_ecommerce

import std.collection.*

class CartItem {
    let product: Product
    var quantity: Int64
    init(product: Product, quantity: Int64) {
        this.product = product
        this.quantity = quantity
    }
    func subtotal(): Int64 {
        return product.price * quantity
    }
    func describe(): String {
        return "${product.name} x${quantity} = ${subtotal()}"
    }
}

class ShoppingCart {
    let customer: Customer
    init(customer: Customer) {
        this.customer = customer
    }
    let items = ArrayList<CartItem>()
    func addItem(product: Product, quantity: Int64) {
        for (item in items) {
            if (item.product.name == product.name) {
                item.quantity += quantity
                return
            }
        }
        items.add(CartItem(product, quantity))
    }
    func total(): Int64 {
        var sum = 0
        for (item in items) {
            sum += item.subtotal()
        }
        return sum
    }
    func itemCount(): Int64 {
        var count = 0
        for (item in items) {
            count += item.quantity
        }
        return count
    }
    func printCart() {
        println("Cart for ${customer.name}:")
        for (item in items) {
            println("  ${item.describe()}")
        }
        println("  Total: ${total()}")
    }
}

class Customer {
    let name: String
    let id: Int64
    init(name: String, id: Int64) {
        this.name = name
        this.id = id
    }
    var loyaltyPoints: Int64 = 0
    func earnPoints(amount: Int64) {
        loyaltyPoints += amount
    }
    func info(): String {
        return "Customer(${name}, id=${id}, points=${loyaltyPoints})"
    }
}

class Order {
    let orderId: Int64
    let customer: Customer
    let items: ArrayList<CartItem>
    let total: Int64
    init(orderId: Int64, customer: Customer, items: ArrayList<CartItem>, total: Int64) {
        this.orderId = orderId
        this.customer = customer
        this.items = items
        this.total = total
    }
    var status: String = "pending"
    func confirm() {
        status = "confirmed"
        let points = total / 10
        customer.earnPoints(points)
        println("Order #${orderId} confirmed for ${customer.name}, earned ${points} points")
    }
    func describe() {
        println("Order #${orderId} [${status}] - ${customer.name} - ${items.size} items - total: ${total}")
    }
}

class OrderProcessor {
    let orders = ArrayList<Order>()
    var nextOrderId = 1
    func checkout(cart: ShoppingCart): Order {
        let order = Order(nextOrderId, cart.customer, cart.items, cart.total())
        orders.add(order)
        nextOrderId += 1
        return order
    }
    func processAll() {
        for (order in orders) {
            order.confirm()
        }
    }
    func printSummary() {
        println("--- Order Summary ---")
        for (order in orders) {
            order.describe()
        }
        println("Total orders: ${orders.size}")
    }
}

class Product <: ToString {
    let name: String
    let price: Int64
    let stock: Int64
    init(name: String, price: Int64, stock: Int64) {
        this.name = name
        this.price = price
        this.stock = stock
    }
    public func toString(): String {
        return "Product(name=${this.name}, price=${this.price}, stock=${this.stock})"
    }
}

class ProductCatalog {
    let products = ArrayList<Product>()
    func addProduct(product: Product) {
        products.add(product)
    }
    func findByName(name: String): ?Product {
        for (p in products) {
            if (p.name == name) {
                return p
            }
        }
        return None
    }
    func listProducts() {
        for (p in products) {
            println("  ${p.name}: ${p.price} (stock: ${p.stock})")
        }
    }
    func totalProducts(): Int64 {
        return products.size
    }
}

main() {
    let catalog = ProductCatalog()
    catalog.addProduct(Product("Laptop", 999, 10))
    catalog.addProduct(Product("Mouse", 25, 100))
    catalog.addProduct(Product("Keyboard", 75, 50))
    catalog.addProduct(Product("Monitor", 450, 20))
    catalog.addProduct(Product("Headset", 60, 80))
    println("Product Catalog:")
    catalog.listProducts()
    println("Total products: ${catalog.totalProducts()}")
    let alice = Customer("Alice", 1)
    let bob = Customer("Bob", 2)
    let cart1 = ShoppingCart(alice)
    let laptop = catalog.findByName("Laptop")
    if (let Some(laptop) <- laptop) {
        cart1.addItem(laptop, 1)
    }
    let mouse = catalog.findByName("Mouse")
    if (let Some(mouse) <- mouse) {
        cart1.addItem(mouse, 2)
    }
    let cart2 = ShoppingCart(bob)
    let kb = catalog.findByName("Keyboard")
    if (let Some(kb) <- kb) {
        cart2.addItem(kb, 1)
    }
    let headset = catalog.findByName("Headset")
    if (let Some(headset) <- headset) {
        cart2.addItem(headset, 1)
    }
    println()
    cart1.printCart()
    println()
    cart2.printCart()
    println()
    let processor = OrderProcessor()
    let o1 = processor.checkout(cart1)
    let o2 = processor.checkout(cart2)
    processor.processAll()
    println()
    processor.printSummary()
    println()
    println(alice.info())
    println(bob.info())
}