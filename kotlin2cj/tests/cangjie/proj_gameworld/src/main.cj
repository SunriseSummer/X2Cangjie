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

open class Entity {
    let name: String
    var hp: Int64
    let maxHp: Int64
    init(name: String, hp: Int64, maxHp: Int64) {
        this.name = name
        this.hp = hp
        this.maxHp = maxHp
    }
    var alive: Bool = true
    public open func takeDamage(amount: Int64) {
        hp -= amount
        if (hp <= 0) {
            hp = 0
            alive = false
        }
    }
    public open func heal(amount: Int64) {
        if (!alive) {
            return
        }
        hp += amount
        if (hp > maxHp) {
            hp = maxHp
        }
    }
    public open func status(): String {
        let state = if (alive) {
            "alive"
        } else {
            "dead"
        }
        return "${name}: ${hp}/${maxHp} HP (${state})"
    }
}

class Player <: Entity {
    let level: Int64
    init(name: String, hp: Int64, level: Int64) {
        super(name, hp, hp)
        this.level = level
    }
    var xp: Int64 = 0
    var gold: Int64 = 0
    let inventory = ArrayList<String>()
    func gainXp(amount: Int64) {
        xp += amount
        println("  ${name} gained ${amount} XP (total: ${xp})")
    }
    func gainGold(amount: Int64) {
        gold += amount
    }
    func addItem(item: String) {
        inventory.add(item)
    }
    public override func status(): String {
        return "${name}: ${hp}/${maxHp} HP, Level ${level}, XP=${xp}, Gold=${gold}"
    }
    func printInventory() {
        println("${name}'s inventory (${inventory.size} items):")
        for (item in inventory) {
            println("  - ${item}")
        }
    }
}

class World {
    let worldName: String
    init(worldName: String) {
        this.worldName = worldName
    }
    let players = ArrayList<Player>()
    let encounters = ArrayList<Encounter>()
    var battlesCompleted = 0
    func addPlayer(player: Player) {
        players.add(player)
        println("${player.name} enters ${worldName}")
    }
    func addEncounter(encounter: Encounter) {
        encounters.add(encounter)
    }
    func runEncounters(player: Player) {
        for (enc in encounters) {
            if (!player.alive) {
                break
            }
            enc.fight(player)
            if (player.alive) {
                player.heal(20)
                println("  ${player.name} rests and heals. ${player.status()}")
            }
            battlesCompleted += 1
        }
    }
    func printWorldStatus() {
        println("=== World: ${worldName} ===")
        println("Battles completed: ${battlesCompleted}")
        for (p in players) {
            println("  ${p.status()}")
        }
    }
}

main() {
    let world = World("Dungeon")
    let hero = Player("Hero", 100, 3)
    hero.addItem("Sword")
    hero.addItem("Shield")
    hero.addItem("Potion")
    world.addPlayer(hero)
    world.addEncounter(Encounter(Enemy("Goblin", 30, 8, 10, 5)))
    world.addEncounter(Encounter(Enemy("Skeleton", 50, 12, 20, 10)))
    world.addEncounter(Encounter(Enemy("Dragon", 80, 25, 50, 30)))
    println()
    hero.printInventory()
    println()
    world.runEncounters(hero)
    println()
    world.printWorldStatus()
    println()
    println("Final: ${hero.status()}")
    println("Gold collected: ${hero.gold}")
}