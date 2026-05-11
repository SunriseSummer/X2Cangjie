// Tic-Tac-Toe with a tiny minimax AI (~190 lines).  Exercises classes,
// enums, ArrayList<T>, recursion, switch/match, optional return, and
// formatted output.  Plays a fixed game (deterministic) so we can have a
// stable .expected output.

enum Cell { Empty, X, O }
enum Winner { None, XWins, OWins, Draw }

function otherSide(c: Cell): Cell {
    switch (c) {
        case Cell.X: return Cell.O;
        case Cell.O: return Cell.X;
        default: return Cell.Empty;
    }
}

function cellChar(c: Cell): string {
    switch (c) {
        case Cell.X: return "X";
        case Cell.O: return "O";
        default: return ".";
    }
}

class Board {
    cells: ArrayList<Cell>;

    constructor() {
        this.cells = new ArrayList<Cell>();
        for (let i = 0; i < 9; i++) {
            this.cells.push(Cell.Empty);
        }
    }

    get(r: number, c: number): Cell {
        return this.cells[r * 3 + c];
    }

    setAt(r: number, c: number, v: Cell): void {
        this.cells[r * 3 + c] = v;
    }

    isFull(): boolean {
        for (const v of this.cells) {
            switch (v) {
                case Cell.Empty: return false;
                default: break;
            }
        }
        return true;
    }

    lineHas(a: number, b: number, c: number, who: Cell): boolean {
        return sameCell(this.cells[a], who)
            && sameCell(this.cells[b], who)
            && sameCell(this.cells[c], who);
    }

    winnerFor(who: Cell): boolean {
        let r: number;
        for (r = 0; r < 3; r++) {
            if (this.lineHas(r * 3, r * 3 + 1, r * 3 + 2, who)) return true;
        }
        for (r = 0; r < 3; r++) {
            if (this.lineHas(r, r + 3, r + 6, who)) return true;
        }
        if (this.lineHas(0, 4, 8, who)) return true;
        if (this.lineHas(2, 4, 6, who)) return true;
        return false;
    }

    judge(): Winner {
        if (this.winnerFor(Cell.X)) return Winner.XWins;
        if (this.winnerFor(Cell.O)) return Winner.OWins;
        if (this.isFull()) return Winner.Draw;
        return Winner.None;
    }

    render(): string {
        let out: string = "";
        for (let r = 0; r < 3; r++) {
            for (let c = 0; c < 3; c++) {
                out = out + cellChar(this.get(r, c));
            }
            out = out + "\n";
        }
        return out;
    }
}

function sameCell(a: Cell, b: Cell): boolean {
    switch (a) {
        case Cell.X:
            switch (b) { case Cell.X: return true; default: return false; }
        case Cell.O:
            switch (b) { case Cell.O: return true; default: return false; }
        default:
            switch (b) { case Cell.Empty: return true; default: return false; }
    }
}

// Minimax: returns score from the perspective of side "X".  +1 for X win,
// -1 for O win, 0 otherwise.  ``toMove`` is whose turn it is.
function score(b: Board, toMove: Cell, depth: number): number {
    const w: Winner = b.judge();
    switch (w) {
        case Winner.XWins: return 10 - depth;
        case Winner.OWins: return depth - 10;
        case Winner.Draw:  return 0;
        default: break;
    }
    let best: number = -1000;
    let r: number;
    let c: number;
    let movedSign: number = 1;
    switch (toMove) {
        case Cell.O: movedSign = -1; break;
        default: movedSign = 1;
    }
    if (movedSign === -1) {
        best = 1000;
    }
    for (r = 0; r < 3; r++) {
        for (c = 0; c < 3; c++) {
            switch (b.get(r, c)) {
                case Cell.Empty:
                    b.setAt(r, c, toMove);
                    const s: number = score(b, otherSide(toMove), depth + 1);
                    b.setAt(r, c, Cell.Empty);
                    if (movedSign === 1) {
                        if (s > best) best = s;
                    } else {
                        if (s < best) best = s;
                    }
                    break;
                default: break;
            }
        }
    }
    return best;
}

function bestMoveCell(b: Board, side: Cell): number {
    let bestIdx: number = -1;
    let bestScore: number = -10000;
    let sign: number = 1;
    switch (side) {
        case Cell.O: sign = -1; break;
        default: sign = 1;
    }
    if (sign === -1) {
        bestScore = 10000;
    }
    for (let i = 0; i < 9; i++) {
        const r: number = ((i) / 3);
        const c: number = i - r * 3;
        switch (b.get(r, c)) {
            case Cell.Empty:
                b.setAt(r, c, side);
                const s: number = score(b, otherSide(side), 1);
                b.setAt(r, c, Cell.Empty);
                if (sign === 1) {
                    if (s > bestScore) { bestScore = s; bestIdx = i; }
                } else {
                    if (s < bestScore) { bestScore = s; bestIdx = i; }
                }
                break;
            default: break;
        }
    }
    return bestIdx;
}

function play(): string {
    const b: Board = new Board();
    let toMove: Cell = Cell.X;
    let moves: number = 0;
    while (true) {
        const w: Winner = b.judge();
        switch (w) {
            case Winner.XWins: return `X wins in ${moves}\n${b.render()}`;
            case Winner.OWins: return `O wins in ${moves}\n${b.render()}`;
            case Winner.Draw:  return `Draw in ${moves}\n${b.render()}`;
            default: break;
        }
        const m: number = bestMoveCell(b, toMove);
        const r: number = ((m) / 3);
        const c: number = m - r * 3;
        b.setAt(r, c, toMove);
        toMove = otherSide(toMove);
        moves = moves + 1;
    }
    return "?";
}

console.log(play());
