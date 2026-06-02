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
