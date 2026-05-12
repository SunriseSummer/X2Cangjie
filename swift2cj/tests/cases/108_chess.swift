// Large #2 (iter5): simple chess-like board + piece movement validator (~300 lines).
enum Color { case white; case black }

enum PieceKind { case king; case queen; case rook; case bishop; case knight; case pawn }

class Piece {
    let kind: PieceKind
    let color: Color
    init(_ k: PieceKind, _ c: Color) {
        self.kind = k
        self.color = c
    }
    func sym() -> String {
        switch kind {
        case .king:   return color == .white ? "K" : "k"
        case .queen:  return color == .white ? "Q" : "q"
        case .rook:   return color == .white ? "R" : "r"
        case .bishop: return color == .white ? "B" : "b"
        case .knight: return color == .white ? "N" : "n"
        case .pawn:   return color == .white ? "P" : "p"
        }
    }
}

class Board {
    // 8x8, row 0 = white's back rank, row 7 = black's back rank
    var grid: [[Piece?]] = []

    init() {
        var i = 0
        while i < 8 {
            var row: [Piece?] = []
            var j = 0
            while j < 8 {
                row.append(nil)
                j += 1
            }
            grid.append(row)
            i += 1
        }
    }

    func place(_ p: Piece, _ r: Int, _ c: Int) {
        grid[r][c] = p
    }

    func at(_ r: Int, _ c: Int) -> Piece? {
        if r < 0 || r > 7 || c < 0 || c > 7 {
            return nil
        }
        return grid[r][c]
    }

    func inBounds(_ r: Int, _ c: Int) -> Bool {
        return r >= 0 && r < 8 && c >= 0 && c < 8
    }

    // Check whether *piece* could move from (fr,fc) to (tr,tc) given current
    // board state.  No castling, en-passant or promotion.
    func canMove(_ fr: Int, _ fc: Int, _ tr: Int, _ tc: Int) -> Bool {
        if !inBounds(fr, fc) || !inBounds(tr, tc) {
            return false
        }
        if fr == tr && fc == tc {
            return false
        }
        let mp = at(fr, fc)
        guard let p = mp else { return false }
        let dest = at(tr, tc)
        if let d = dest {
            if d.color == p.color {
                return false
            }
        }
        let dr = tr - fr
        let dc = tc - fc
        let adr = dr < 0 ? -dr : dr
        let adc = dc < 0 ? -dc : dc
        switch p.kind {
        case .king:
            return adr <= 1 && adc <= 1
        case .knight:
            return (adr == 2 && adc == 1) || (adr == 1 && adc == 2)
        case .rook:
            if dr != 0 && dc != 0 {
                return false
            }
            return pathClear(fr, fc, tr, tc)
        case .bishop:
            if adr != adc {
                return false
            }
            return pathClear(fr, fc, tr, tc)
        case .queen:
            if !(dr == 0 || dc == 0 || adr == adc) {
                return false
            }
            return pathClear(fr, fc, tr, tc)
        case .pawn:
            let forward = p.color == .white ? 1 : -1
            let startRow = p.color == .white ? 1 : 6
            // Quiet move
            if dc == 0 {
                if dr == forward && dest == nil {
                    return true
                }
                if fr == startRow && dr == 2 * forward {
                    let mid = at(fr + forward, fc)
                    if mid == nil && dest == nil {
                        return true
                    }
                }
                return false
            }
            // Capture
            if adc == 1 && dr == forward {
                if let _ = dest {
                    return true
                }
                return false
            }
            return false
        }
    }

    func pathClear(_ fr: Int, _ fc: Int, _ tr: Int, _ tc: Int) -> Bool {
        let dr = tr - fr
        let dc = tc - fc
        let steps = max(dr < 0 ? -dr : dr, dc < 0 ? -dc : dc)
        let sr = dr == 0 ? 0 : (dr > 0 ? 1 : -1)
        let sc = dc == 0 ? 0 : (dc > 0 ? 1 : -1)
        var i = 1
        while i < steps {
            let p = at(fr + sr * i, fc + sc * i)
            if p != nil {
                return false
            }
            i += 1
        }
        return true
    }

    func render() -> String {
        var s = ""
        var r = 7
        while r >= 0 {
            var c = 0
            while c < 8 {
                let p = at(r, c)
                if let pp = p {
                    s = s + pp.sym()
                } else {
                    s = s + "."
                }
                c += 1
            }
            s = s + "\n"
            r -= 1
        }
        return s
    }
}

let b = Board()
b.place(Piece(.king,   .white), 0, 4)
b.place(Piece(.queen,  .white), 0, 3)
b.place(Piece(.rook,   .white), 0, 0)
b.place(Piece(.rook,   .white), 0, 7)
b.place(Piece(.knight, .white), 0, 1)
b.place(Piece(.bishop, .white), 0, 2)
b.place(Piece(.pawn,   .white), 1, 4)
b.place(Piece(.pawn,   .white), 1, 0)

b.place(Piece(.king,   .black), 7, 4)
b.place(Piece(.queen,  .black), 7, 3)
b.place(Piece(.rook,   .black), 7, 0)
b.place(Piece(.knight, .black), 7, 6)
b.place(Piece(.pawn,   .black), 6, 4)
b.place(Piece(.pawn,   .black), 4, 3)   // capture target

print(b.render())

// Probe assorted moves.
let moves: [(Int, Int, Int, Int, String)] = [
    (1, 4, 3, 4, "pawn e2->e4"),
    (1, 4, 2, 4, "pawn e2->e3"),
    (1, 4, 4, 4, "pawn jumps 3"),
    (0, 1, 2, 2, "knight b1->c3"),
    (0, 1, 2, 0, "knight b1->a3"),
    (0, 4, 1, 5, "king blocked by own"),
    (0, 0, 5, 0, "rook a1->a6 (blocked by pawn)"),
    (0, 0, 0, 5, "rook a1 across own"),
    (7, 0, 0, 7, "rook a8 diag invalid"),
    (1, 0, 2, 1, "white pawn capture empty"),
    (4, 3, 3, 4, "black pawn capture white e4 (none yet)"),
    (0, 3, 4, 7, "queen d1 -> h5"),
    (0, 3, 5, 3, "queen d1 -> d6 (blocked)"),
    (0, 2, 4, 6, "bishop c1 -> g5"),
    (0, 2, 4, 0, "bishop c1 -> a5 invalid"),
]
for m in moves {
    let ok = b.canMove(m.0, m.1, m.2, m.3)
    print("\(m.4): \(ok)")
}
