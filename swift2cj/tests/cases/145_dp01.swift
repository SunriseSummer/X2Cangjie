import Foundation

// ============================================
// 01 背包动态规划求解
// ============================================

/// 基础版：返回最大价值（一维 DP，空间优化）
func knapsack01(weights: [Int], values: [Int], capacity: Int) -> Int {
    let n = weights.count
    guard n > 0, capacity > 0 else { return 0 }
    
    // dp[w] 表示容量为 w 时的最大价值
    var dp = Array(repeating: 0, count: capacity + 1)
    
    for i in 0..<n {
        // 必须倒序遍历，防止同一物品被重复选取
        for w in stride(from: capacity, through: weights[i], by: -1) {
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
        }
    }
    
    return dp[capacity]
}

/// 完整版：返回最大价值 + 选中的物品索引（二维 DP，便于回溯）
func knapsack01WithSelection(weights: [Int], values: [Int], capacity: Int) -> (maxValue: Int, selectedItems: [Int]) {
    let n = weights.count
    guard n > 0, capacity > 0 else { return (0, []) }
    
    // dp[i][w] 表示前 i 个物品、容量为 w 时的最大价值
    var dp = Array(repeating: Array(repeating: 0, count: capacity + 1), count: n + 1)
    
    for i in 1...n {
        for w in 0...capacity {
            if weights[i - 1] <= w {
                dp[i][w] = max(
                    dp[i - 1][w],                                    // 不选第 i 个物品
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]    // 选第 i 个物品
                )
            } else {
                dp[i][w] = dp[i - 1][w]  // 装不下，只能不选
            }
        }
    }
    
    // 回溯找出选中的物品
    var selected: [Int] = []
    var w = capacity
    for i in stride(from: n, to: 0, by: -1) {
        if dp[i][w] != dp[i - 1][w] {
            selected.append(i - 1)
            w -= weights[i - 1]
        }
    }
    
    return (dp[n][capacity], selected.reversed())
}

// ============================================
// 测试用例
// ============================================

let weights = [2, 3, 4, 5]
let values = [3, 4, 5, 6]
let capacity = 8

// 基础版
let maxValue = knapsack01(weights: weights, values: values, capacity: capacity)
print("最大价值: \(maxValue)")  // 输出: 10

// 完整版
let result = knapsack01WithSelection(weights: weights, values: values, capacity: capacity)
print("最大价值: \(result.maxValue)")       // 输出: 10
print("选中物品: \(result.selectedItems)")  // 输出: [1, 3]
// 验证: 重量 3+5=8 ≤ 8, 价值 4+6=10
