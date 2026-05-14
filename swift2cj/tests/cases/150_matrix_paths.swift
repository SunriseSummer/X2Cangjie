// Large #1 (iter12): grid path count with obstacles using DP
func countPaths(_ grid: [[Int]]) -> Int {
    let rows = grid.count
    if rows == 0 { return 0 }
    let cols = grid[0].count
    if cols == 0 { return 0 }
    var dp = Array(repeating: Array(repeating: 0, count: cols), count: rows)
    if grid[0][0] == 1 { return 0 }
    dp[0][0] = 1
    var r = 0
    while r < rows {
        var c = 0
        while c < cols {
            if grid[r][c] == 1 {
                dp[r][c] = 0
            } else {
                if r > 0 { dp[r][c] += dp[r - 1][c] }
                if c > 0 { dp[r][c] += dp[r][c - 1] }
            }
            c += 1
        }
        r += 1
    }
    return dp[rows - 1][cols - 1]
}

let grid = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
print("paths=\(countPaths(grid))")
