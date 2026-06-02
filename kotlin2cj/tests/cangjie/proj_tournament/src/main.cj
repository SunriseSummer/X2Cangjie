package proj_tournament

import std.collection.*

class Match {
    let player1: TournPlayer
    let player2: TournPlayer
    init(player1: TournPlayer, player2: TournPlayer) {
        this.player1 = player1
        this.player2 = player2
    }
    var winner: ?TournPlayer = None
    var score1: Int64 = 0
    var score2: Int64 = 0
    func play() {
        score1 = (player1.skill * 3) + player1.name.size
        score2 = (player2.skill * 3) + player2.name.size
        if (score1 >= score2) {
            winner = player1
            player1.wins += 1
            player2.losses += 1
        } else {
            winner = player2
            player2.wins += 1
            player1.losses += 1
        }
    }
    func result(): String {
        let w = winner
        if (let Some(w) <- w) {
            return "${player1.name} vs ${player2.name}: ${score1}-${score2} (Winner: ${w.name})"
        }
        return "${player1.name} vs ${player2.name}: not played"
    }
}

class TournPlayer <: ToString {
    let name: String
    let skill: Int64
    init(name: String, skill: Int64) {
        this.name = name
        this.skill = skill
    }
    var wins: Int64 = 0
    var losses: Int64 = 0
    func record(): String {
        return "${wins}-${losses}"
    }
    func describe(): String {
        return "${name} (skill=${skill}, record=${record()})"
    }
    public func toString(): String {
        return "TournPlayer(name=${this.name}, skill=${this.skill})"
    }
}

class Tournament {
    let tournName: String
    init(tournName: String) {
        this.tournName = tournName
    }
    let players = ArrayList<TournPlayer>()
    let matches = ArrayList<Match>()
    var roundNumber = 0
    func addPlayer(player: TournPlayer) {
        players.add(player)
    }
    func runRoundRobin() {
        println("=== ${tournName} Round Robin ===")
        for (i in 0..players.size) {
            for (j in (i + 1)..players.size) {
                roundNumber += 1
                let m = Match(players[i], players[j])
                m.play()
                matches.add(m)
                println("  Match ${roundNumber}: ${m.result()}")
            }
        }
    }
    func findChampion(): ?TournPlayer {
        if (players.isEmpty()) {
            return None
        }
        var best = players[0]
        for (i in 1..players.size) {
            if (players[i].wins > best.wins) {
                best = players[i]
            }
        }
        return best
    }
    func printStandings() {
        println("=== Standings ===")
        let sorted = ArrayList<TournPlayer>()
        for (p in players) {
            sorted.add(p)
        }
        for (i in 0..sorted.size) {
            for (j in (i + 1)..sorted.size) {
                if (sorted[j].wins > sorted[i].wins) {
                    let tmp = sorted[i]
                    sorted[i] = sorted[j]
                    sorted[j] = tmp
                }
            }
        }
        var rank = 1
        for (p in sorted) {
            println("  #${rank} ${p.describe()}")
            rank += 1
        }
    }
    func printMatchHistory() {
        println("=== Match History (${matches.size} matches) ===")
        for (m in matches) {
            println("  ${m.result()}")
        }
    }
}

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