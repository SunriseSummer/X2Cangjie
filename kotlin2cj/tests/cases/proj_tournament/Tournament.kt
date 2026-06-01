class Tournament(val tournName: String) {
    val players = mutableListOf<TournPlayer>()
    val matches = mutableListOf<Match>()
    var roundNumber = 0

    fun addPlayer(player: TournPlayer) {
        players.add(player)
    }

    fun runRoundRobin() {
        println("=== $tournName Round Robin ===")
        for (i in 0 until players.size) {
            for (j in i + 1 until players.size) {
                roundNumber++
                val m = Match(players[i], players[j])
                m.play()
                matches.add(m)
                println("  Match $roundNumber: ${m.result()}")
            }
        }
    }

    fun findChampion(): TournPlayer? {
        if (players.isEmpty()) return null
        var best = players[0]
        for (i in 1 until players.size) {
            if (players[i].wins > best.wins) {
                best = players[i]
            }
        }
        return best
    }

    fun printStandings() {
        println("=== Standings ===")
        // Sort by wins (bubble sort)
        val sorted = mutableListOf<TournPlayer>()
        for (p in players) {
            sorted.add(p)
        }
        for (i in 0 until sorted.size) {
            for (j in i + 1 until sorted.size) {
                if (sorted[j].wins > sorted[i].wins) {
                    val tmp = sorted[i]
                    sorted[i] = sorted[j]
                    sorted[j] = tmp
                }
            }
        }
        var rank = 1
        for (p in sorted) {
            println("  #$rank ${p.describe()}")
            rank++
        }
    }

    fun printMatchHistory() {
        println("=== Match History (${matches.size} matches) ===")
        for (m in matches) {
            println("  ${m.result()}")
        }
    }
}
