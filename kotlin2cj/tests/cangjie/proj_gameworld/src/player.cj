package proj_gameworld

import std.collection.*

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
