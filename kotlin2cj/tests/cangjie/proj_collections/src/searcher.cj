package proj_collections

import std.collection.*
import std.sort.*

class Searcher {
    let items: ArrayList<Int64>
    init(items: ArrayList<Int64>) {
        this.items = items
    }
    func firstPositive(): Int64 {
        return ({ => var _i = 0; for (_e in items) { if (({ it => it > 0 })(_e)) { return _i }; _i++ }; return -1 })()
    }
    func lastPositive(): Int64 {
        return ({ => var _r = -1; var _i = 0; for (_e in items) { if (({ it => it > 0 })(_e)) { _r = _i }; _i++ }; return _r })()
    }
    func hasNegative(): Bool {
        return items.iterator().any({ it => it < 0 })
    }
    func allPositive(): Bool {
        return !items.iterator().any({ it => it < 0 })
    }
    func top3(): ArrayList<Int64> {
        return collectArrayList(({ => let _s = collectArrayList(({ => let _s = collectArrayList(items.iterator()); sort(_s, stable: true); _s })().iterator()); _s.reverse(); _s })().iterator().take(3))
    }
    func skip2(): ArrayList<Int64> {
        return collectArrayList(items.iterator().skip(2))
    }
}
