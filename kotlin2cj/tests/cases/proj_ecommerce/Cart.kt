class CartItem(val product: Product, var quantity: Int) {
    fun subtotal(): Int = product.price * quantity

    fun describe(): String {
        return "${product.name} x$quantity = ${subtotal()}"
    }
}

class ShoppingCart(val customer: Customer) {
    val items = mutableListOf<CartItem>()

    fun addItem(product: Product, quantity: Int) {
        for (item in items) {
            if (item.product.name == product.name) {
                item.quantity += quantity
                return
            }
        }
        items.add(CartItem(product, quantity))
    }

    fun total(): Int {
        var sum = 0
        for (item in items) {
            sum += item.subtotal()
        }
        return sum
    }

    fun itemCount(): Int {
        var count = 0
        for (item in items) {
            count += item.quantity
        }
        return count
    }

    fun printCart() {
        println("Cart for ${customer.name}:")
        for (item in items) {
            println("  ${item.describe()}")
        }
        println("  Total: ${total()}")
    }
}
