fun main() {
    val world = World("Dungeon")

    val hero = Player("Hero", 100, 3)
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
