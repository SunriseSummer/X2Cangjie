fun main() {
    val tourn = Tournament("Champions Cup")

    tourn.addPlayer(TournPlayer("Alice", 8))
    tourn.addPlayer(TournPlayer("Bob", 6))
    tourn.addPlayer(TournPlayer("Charlie", 9))
    tourn.addPlayer(TournPlayer("Diana", 7))
    tourn.addPlayer(TournPlayer("Eve", 5))

    tourn.runRoundRobin()

    println()
    tourn.printStandings()

    println()
    val champ = tourn.findChampion()
    if (champ != null) {
        println("Champion: ${champ.name} with ${champ.wins} wins!")
    }

    println()
    tourn.printMatchHistory()

    println()
    println("Total matches played: ${tourn.matches.size}")
}
