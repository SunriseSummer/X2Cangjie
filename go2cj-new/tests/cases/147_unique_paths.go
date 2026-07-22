package main

import "fmt"

func uniquePaths(n, m int) int {
dp := make([][]int, n)
for i := 0; i < n; i++ {
dp[i] = make([]int, m)
}
for i := 0; i < n; i++ {
dp[i][0] = 1
}
for j := 0; j < m; j++ {
dp[0][j] = 1
}
for i := 1; i < n; i++ {
for j := 1; j < m; j++ {
dp[i][j] = dp[i-1][j] + dp[i][j-1]
}
}
return dp[n-1][m-1]
}

func main() {
fmt.Println(uniquePaths(3, 7))
fmt.Println(uniquePaths(5, 5))
fmt.Println(uniquePaths(2, 10))
}
