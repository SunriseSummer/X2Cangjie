open class Entity(val name: String, var hp: Int, val maxHp: Int) {
    var alive: Boolean = true

    fun takeDamage(amount: Int) {
        hp -= amount
        if (hp <= 0) {
            hp = 0
            alive = false
        }
    }

    fun heal(amount: Int) {
        if (!alive) return
        hp += amount
        if (hp > maxHp) hp = maxHp
    }

    open fun status(): String {
        val state = if (alive) "alive" else "dead"
        return "$name: $hp/$maxHp HP ($state)"
    }
}
