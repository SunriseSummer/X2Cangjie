// Test: Enum with methods and companion-like usage
enum class Season(val months: Int) {
    SPRING(3),
    SUMMER(3),
    AUTUMN(3),
    WINTER(3);

    fun displayName(): String {
        return when (this) {
            SPRING -> "Spring"
            SUMMER -> "Summer"
            AUTUMN -> "Autumn"
            WINTER -> "Winter"
        }
    }
}

fun main() {
    val seasons = listOf(Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER)
    for (s in seasons) {
        println("${s}: ${s.months} months")
    }

    // Enum comparison
    val current = Season.SUMMER
    println("Is summer? ${current == Season.SUMMER}")
    println("Is winter? ${current == Season.WINTER}")
}
