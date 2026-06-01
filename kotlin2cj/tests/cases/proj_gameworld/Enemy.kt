class Enemy(name: String, hp: Int, val damage: Int, val xpReward: Int, val goldReward: Int) : Entity(name, hp, hp) {
    override fun status(): String {
        val state = if (alive) "alive" else "defeated"
        return "Enemy $name: $hp/$maxHp HP, dmg=$damage ($state)"
    }
}

class Encounter(val enemy: Enemy) {
    fun fight(player: Player) {
        println("--- Battle: ${player.name} vs ${enemy.name} ---")
        while (player.alive && enemy.alive) {
            // Player attacks first
            val playerDmg = 10 + player.level * 5
            enemy.takeDamage(playerDmg)
            println("  ${player.name} hits ${enemy.name} for $playerDmg damage")
            if (!enemy.alive) {
                println("  ${enemy.name} defeated!")
                player.gainXp(enemy.xpReward)
                player.gainGold(enemy.goldReward)
                break
            }
            // Enemy attacks
            player.takeDamage(enemy.damage)
            println("  ${enemy.name} hits ${player.name} for ${enemy.damage} damage")
            if (!player.alive) {
                println("  ${player.name} has fallen!")
                break
            }
        }
        println("  ${player.status()}")
        println("  ${enemy.status()}")
    }
}
