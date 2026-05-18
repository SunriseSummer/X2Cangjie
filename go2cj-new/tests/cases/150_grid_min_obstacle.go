package main

import "fmt"

func minPathObstacle(grid [][]int) int {
n := len(grid)
m := len(grid[0])
const INF = 1 << 30
dp := make([][]int, n)
for i := 0; i < n; i++ {
dp[i] = make([]int, m)
for j := 0; j < m; j++ {
dp[i][j] = INF
}
}
if grid[0][0] == 1 {
return -1
}
dp[0][0] = 0
for i := 0; i < n; i++ {
for j := 0; j < m; j++ {
if grid[i][j] == 1 {
continue
}
if i > 0 && dp[i-1][j]+1 < dp[i][j] {
dp[i][j] = dp[i-1][j] + 1
}
if j > 0 && dp[i][j-1]+1 < dp[i][j] {
dp[i][j] = dp[i][j-1] + 1
}
}
}
if dp[n-1][m-1] >= INF {
return -1
}
return dp[n-1][m-1]
}

func main() {
g1 := [][]int{{0, 0, 0}, {1, 1, 0}, {0, 0, 0}}
g2 := [][]int{{0, 1, 0}, {0, 1, 0}, {0, 0, 0}}
g3 := [][]int{{0, 1}, {1, 0}}
fmt.Println(minPathObstacle(g1))
fmt.Println(minPathObstacle(g2))
fmt.Println(minPathObstacle(g3))
}
