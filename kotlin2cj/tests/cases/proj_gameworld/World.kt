class World(val worldName: String) {
    val players = mutableListOf<Player>()
    val encounters = mutableListOf<Encounter>()
    var battlesCompleted = 0

    fun addPlayer(player: Player) {
        players.add(player)
        println("${player.name} enters $worldName")
    }

    fun addEncounter(encounter: Encounter) {
        encounters.add(encounter)
    }

    fun runEncounters(player: Player) {
        for (enc in encounters) {
            if (!player.alive) break
            enc.fight(player)
            if (player.alive) {
                player.heal(20)
                println("  ${player.name} rests and heals. ${player.status()}")
            }
            battlesCompleted++
        }
    }

    fun printWorldStatus() {
        println("=== World: $worldName ===")
        println("Battles completed: $battlesCompleted")
        for (p in players) {
            println("  ${p.status()}")
        }
    }
}
