class Match(val player1: TournPlayer, val player2: TournPlayer) {
    var winner: TournPlayer? = null
    var score1: Int = 0
    var score2: Int = 0

    fun play() {
        // Deterministic scoring based on skill
        score1 = player1.skill * 3 + player1.name.length
        score2 = player2.skill * 3 + player2.name.length
        if (score1 >= score2) {
            winner = player1
            player1.wins++
            player2.losses++
        } else {
            winner = player2
            player2.wins++
            player1.losses++
        }
    }

    fun result(): String {
        val w = winner
        if (w != null) {
            return "${player1.name} vs ${player2.name}: $score1-$score2 (Winner: ${w.name})"
        }
        return "${player1.name} vs ${player2.name}: not played"
    }
}
