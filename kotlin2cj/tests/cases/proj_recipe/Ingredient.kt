data class Ingredient(val name: String, val amount: Int, val unit: String) {
    fun describe(): String = "$amount $unit $name"

    fun scale(factor: Int): Ingredient {
        return Ingredient(name, amount * factor, unit)
    }
}
