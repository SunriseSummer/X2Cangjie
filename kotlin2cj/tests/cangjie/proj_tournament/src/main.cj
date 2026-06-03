package proj_tournament

import std.collection.*

main() {
    let tourn = Tournament("Champions Cup")
    tourn.addPlayer(TournPlayer("Alice", 8))
    tourn.addPlayer(TournPlayer("Bob", 6))
    tourn.addPlayer(TournPlayer("Charlie", 9))
    tourn.addPlayer(TournPlayer("Diana", 7))
    tourn.addPlayer(TournPlayer("Eve", 5))
    tourn.runRoundRobin()
    println()
    tourn.printStandings()
    println()
    let champ = tourn.findChampion()
    if (let Some(champ) <- champ) {
        println("Champion: ${champ.name} with ${champ.wins} wins!")
    }
    println()
    tourn.printMatchHistory()
    println()
    println("Total matches played: ${tourn.matches.size}")
}
