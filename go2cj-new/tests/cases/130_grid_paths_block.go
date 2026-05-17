package main

import "fmt"

func countPaths(grid [][]int) int {
n := len(grid)
m := len(grid[0])
dp := make([][]int, n)
for i := 0; i < n; i++ {
dp[i] = make([]int, m)
}
if grid[0][0] == 1 {
return 0
}
dp[0][0] = 1
for i := 0; i < n; i++ {
for j := 0; j < m; j++ {
if grid[i][j] == 1 {
dp[i][j] = 0
continue
}
if i > 0 {
dp[i][j] = dp[i][j] + dp[i-1][j]
}
if j > 0 {
dp[i][j] = dp[i][j] + dp[i][j-1]
}
}
}
return dp[n-1][m-1]
}

func main() {
g1 := [][]int{{0, 0, 0}, {0, 0, 0}, {0, 0, 0}}
g2 := [][]int{{0, 0, 0}, {0, 1, 0}, {0, 0, 0}}
g3 := [][]int{{1, 0}, {0, 0}}
fmt.Println(countPaths(g1))
fmt.Println(countPaths(g2))
fmt.Println(countPaths(g3))
}
