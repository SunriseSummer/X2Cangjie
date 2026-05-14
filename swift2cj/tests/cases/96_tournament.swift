// Large #2 (iter4): single-elimination tournament bracket simulator (~250 lines)
class Team {
    let name: String
    let skill: Int
    var wins: Int = 0
    var losses: Int = 0

    init(name: String, skill: Int) {
        self.name = name
        self.skill = skill
    }
}

class Match {
    let round: Int
    let id: Int
    let a: Team
    let b: Team
    var winner: Team? = nil
    var score: String = ""

    init(round: Int, id: Int, a: Team, b: Team) {
        self.round = round
        self.id = id
        self.a = a
        self.b = b
    }

    func play(_ randSeed: Int) {
        // Deterministic: higher skill + a seed-dependent bonus wins
        let bonusA = (randSeed * 13 + id * 7) % 5
        let bonusB = (randSeed * 17 + id * 11) % 5
        let scoreA = a.skill + bonusA
        let scoreB = b.skill + bonusB
        if scoreA >= scoreB {
            winner = a
            a.wins += 1
            b.losses += 1
        } else {
            winner = b
            b.wins += 1
            a.losses += 1
        }
        score = "\(scoreA)-\(scoreB)"
    }

    func summary() -> String {
        let w = winner!
        return "R\(round)M\(id): \(a.name)(\(a.skill)) vs \(b.name)(\(b.skill)) -> \(w.name) [\(score)]"
    }
}

class Tournament {
    var teams: [Team]
    var rounds: [[Match]] = []
    let seed: Int
    var nextMatchId: Int = 1

    init(teams: [Team], seed: Int) {
        self.teams = teams
        self.seed = seed
    }

    func run() {
        var current = teams
        var roundNum = 1
        while current.count >= 2 {
            var matches: [Match] = []
            var i = 0
            while i + 1 < current.count {
                let m = Match(round: roundNum, id: nextMatchId, a: current[i], b: current[i + 1])
                nextMatchId += 1
                m.play(seed + roundNum)
                matches.append(m)
                i += 2
            }
            var winners: [Team] = []
            for m in matches {
                winners.append(m.winner!)
            }
            // odd team gets a bye into the next round
            if current.count % 2 == 1 {
                winners.append(current[current.count - 1])
            }
            rounds.append(matches)
            current = winners
            roundNum += 1
        }
    }

    func champion() -> Team {
        // The last surviving team after all rounds.
        var last = teams
        for ms in rounds {
            var winners: [Team] = []
            for m in ms {
                winners.append(m.winner!)
            }
            if last.count % 2 == 1 {
                winners.append(last[last.count - 1])
            }
            last = winners
        }
        return last[0]
    }

    func dump() {
        for ms in rounds {
            for m in ms {
                print(m.summary())
            }
        }
    }

    func leaderboard() {
        for t in teams {
            print("\(t.name) skill=\(t.skill) W=\(t.wins) L=\(t.losses)")
        }
    }
}

let teams: [Team] = [
    Team(name: "Alpha", skill: 8),
    Team(name: "Bravo", skill: 5),
    Team(name: "Charlie", skill: 7),
    Team(name: "Delta", skill: 6),
    Team(name: "Echo", skill: 9),
    Team(name: "Foxtrot", skill: 4),
    Team(name: "Golf", skill: 3),
    Team(name: "Hotel", skill: 10)
]

let tour = Tournament(teams: teams, seed: 42)
tour.run()
print("== bracket ==")
tour.dump()
print("== champion: \(tour.champion().name) ==")
print("== leaderboard ==")
tour.leaderboard()
print("rounds played = \(tour.rounds.count)")

// odd number of teams
let small: [Team] = [
    Team(name: "X", skill: 5),
    Team(name: "Y", skill: 3),
    Team(name: "Z", skill: 7)
]
let tour2 = Tournament(teams: small, seed: 1)
tour2.run()
print("== small bracket ==")
tour2.dump()
print("== small champion: \(tour2.champion().name) ==")
