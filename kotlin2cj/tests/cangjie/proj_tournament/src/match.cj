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
