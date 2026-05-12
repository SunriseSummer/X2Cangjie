// Medium #1 (iter7): 0/1 knapsack dynamic programming
class Item {
    let name: String
    let weight: Int
    let value: Int
    init(_ name: String, _ weight: Int, _ value: Int) {
        self.name = name
        self.weight = weight
        self.value = value
    }
}

func knapsack(_ items: [Item], _ cap: Int) -> Int {
    var dp: [Int] = []
    var w = 0
    while w <= cap {
        dp.append(0)
        w += 1
    }
    for item in items {
        var c = cap
        while c >= item.weight {
            let candidate = dp[c - item.weight] + item.value
            if candidate > dp[c] {
                dp[c] = candidate
            }
            c -= 1
        }
    }
    return dp[cap]
}

func chosenGreedy(_ items: [Item], _ cap: Int) -> String {
    var left = cap
    var value = 0
    var names: [String] = []
    for item in items {
        if item.weight <= left {
            left -= item.weight
            value += item.value
            names.append(item.name)
        }
    }
    var joined = ""
    var i = 0
    while i < names.count {
        if i > 0 {
            joined = joined + ","
        }
        joined = joined + names[i]
        i += 1
    }
    return "greedy value=\(value) items=\(joined) left=\(left)"
}

let items = [
    Item("map", 1, 3),
    Item("water", 3, 8),
    Item("food", 2, 6),
    Item("jacket", 2, 5),
    Item("camera", 1, 4),
    Item("book", 1, 2)
]
for cap in [3, 4, 5, 6, 7] {
    print("cap=\(cap) best=\(knapsack(items, cap))")
}
print(chosenGreedy(items, 6))
