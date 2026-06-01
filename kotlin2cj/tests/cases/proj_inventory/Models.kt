enum class Category {
    FOOD,
    ELECTRONICS,
    CLOTHING,
    BOOKS
}

data class Product(val name: String, val price: Double, val category: Category, val quantity: Int)
