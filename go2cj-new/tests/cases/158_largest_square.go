package main

import "fmt"

func maxSquare(grid [][]int) int {
n := len(grid)
m := len(grid[0])
dp := make([][]int, n)
best := 0
for i := 0; i < n; i++ {
dp[i] = make([]int, m)
for j := 0; j < m; j++ {
if grid[i][j] == 0 {
dp[i][j] = 0
continue
}
if i == 0 || j == 0 {
dp[i][j] = 1
} else {
x := dp[i-1][j]
if dp[i][j-1] < x {
x = dp[i][j-1]
}
if dp[i-1][j-1] < x {
x = dp[i-1][j-1]
}
dp[i][j] = x + 1
}
if dp[i][j] > best {
best = dp[i][j]
}
}
}
return best
}

func main() {
g1 := [][]int{{1, 0, 1, 0}, {1, 1, 1, 1}, {1, 1, 1, 1}, {0, 1, 1, 1}}
g2 := [][]int{{0, 0}, {0, 0}}
g3 := [][]int{{1, 1, 1}, {1, 1, 1}}
fmt.Println(maxSquare(g1))
fmt.Println(maxSquare(g2))
fmt.Println(maxSquare(g3))
}
