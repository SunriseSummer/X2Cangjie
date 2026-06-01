class Player(name: String, hp: Int, val level: Int) : Entity(name, hp, hp) {
    var xp: Int = 0
    var gold: Int = 0
    val inventory = mutableListOf<String>()

    fun gainXp(amount: Int) {
        xp += amount
        println("  $name gained $amount XP (total: $xp)")
    }

    fun gainGold(amount: Int) {
        gold += amount
    }

    fun addItem(item: String) {
        inventory.add(item)
    }

    override fun status(): String {
        return "$name: $hp/$maxHp HP, Level $level, XP=$xp, Gold=$gold"
    }

    fun printInventory() {
        println("$name's inventory (${inventory.size} items):")
        for (item in inventory) {
            println("  - $item")
        }
    }
}
