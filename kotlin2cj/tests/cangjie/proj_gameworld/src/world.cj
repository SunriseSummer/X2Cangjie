package proj_gameworld

import std.collection.*

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
