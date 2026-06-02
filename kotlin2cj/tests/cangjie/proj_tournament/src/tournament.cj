package proj_tournament

import std.collection.*

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
