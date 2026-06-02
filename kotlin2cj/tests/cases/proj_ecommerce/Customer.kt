class Customer(val name: String, val id: Int) {
    var loyaltyPoints: Int = 0

    fun earnPoints(amount: Int) {
        loyaltyPoints += amount
    }

    fun info(): String {
        return "Customer($name, id=$id, points=$loyaltyPoints)"
    }
}
