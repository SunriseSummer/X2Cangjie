data class WarehouseItem(val sku: String, val name: String, var quantity: Int, val unitPrice: Int) {
    fun totalValue(): Int = quantity * unitPrice

    fun describe(): String {
        return "$sku: $name (qty=$quantity, unit=$unitPrice, total=${totalValue()})"
    }
}
