package proj_gameworld

import std.collection.*

class Enemy <: Entity {
    let damage: Int64
    let xpReward: Int64
    let goldReward: Int64
    init(name: String, hp: Int64, damage: Int64, xpReward: Int64, goldReward: Int64) {
        super(name, hp, hp)
        this.damage = damage
        this.xpReward = xpReward
        this.goldReward = goldReward
    }
    public override func status(): String {
        let state = if (alive) {
            "alive"
        } else {
            "defeated"
        }
        return "Enemy ${name}: ${hp}/${maxHp} HP, dmg=${damage} (${state})"
    }
}

class Encounter {
    let enemy: Enemy
    init(enemy: Enemy) {
        this.enemy = enemy
    }
    func fight(player: Player) {
        println("--- Battle: ${player.name} vs ${enemy.name} ---")
        while (player.alive && enemy.alive) {
            let playerDmg = 10 + (player.level * 5)
            enemy.takeDamage(playerDmg)
            println("  ${player.name} hits ${enemy.name} for ${playerDmg} damage")
            if (!enemy.alive) {
                println("  ${enemy.name} defeated!")
                player.gainXp(enemy.xpReward)
                player.gainGold(enemy.goldReward)
                break
            }
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
