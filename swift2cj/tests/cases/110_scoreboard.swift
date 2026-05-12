// Small #2 (iter6): scoreboard ranking with tie break
class Score {
    let name: String
    var points: Int
    var wins: Int

    init(_ name: String, _ points: Int, _ wins: Int) {
        self.name = name
        self.points = points
        self.wins = wins
    }

    func betterThan(_ other: Score) -> Bool {
        if points != other.points {
            return points > other.points
        }
        if wins != other.wins {
            return wins > other.wins
        }
        return name < other.name
    }

    func line(_ rank: Int) -> String {
        return "#\(rank) \(name) pts=\(points) wins=\(wins)"
    }
}

func sortScores(_ xs: [Score]) -> [Score] {
    var out: [Score] = []
    for x in xs {
        var i = 0
        while i < out.count && !x.betterThan(out[i]) {
            i += 1
        }
        out.insert(x, at: i)
    }
    return out
}

let scores = [
    Score("red", 10, 3),
    Score("blue", 12, 2),
    Score("green", 10, 5),
    Score("yellow", 12, 2),
    Score("black", 7, 4)
]
let ranked = sortScores(scores)
var i = 0
while i < ranked.count {
    print(ranked[i].line(i + 1))
    i += 1
}
