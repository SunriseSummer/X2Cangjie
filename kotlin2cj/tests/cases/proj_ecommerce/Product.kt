data class Product(val name: String, val price: Int, val stock: Int)

class ProductCatalog {
    val products = mutableListOf<Product>()

    fun addProduct(product: Product) {
        products.add(product)
    }

    fun findByName(name: String): Product? {
        for (p in products) {
            if (p.name == name) return p
        }
        return null
    }

    fun listProducts() {
        for (p in products) {
            println("  ${p.name}: ${p.price} (stock: ${p.stock})")
        }
    }

    fun totalProducts(): Int = products.size
}
