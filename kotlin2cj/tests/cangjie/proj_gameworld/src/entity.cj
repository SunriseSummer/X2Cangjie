package proj_gameworld

import std.collection.*

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
