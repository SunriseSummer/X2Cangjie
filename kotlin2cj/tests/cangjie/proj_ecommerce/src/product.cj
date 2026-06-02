package proj_ecommerce

import std.collection.*

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
