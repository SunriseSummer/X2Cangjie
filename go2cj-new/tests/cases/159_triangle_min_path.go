package main

import "fmt"

func minPath(tri [][]int) int {
n := len(tri)
dp := make([][]int, n)
for i := 0; i < n; i++ {
dp[i] = make([]int, len(tri[i]))
}
dp[0][0] = tri[0][0]
for i := 1; i < n; i++ {
for j := 0; j < len(tri[i]); j++ {
if j == 0 {
dp[i][j] = dp[i-1][j] + tri[i][j]
} else if j == len(tri[i])-1 {
dp[i][j] = dp[i-1][j-1] + tri[i][j]
} else {
a := dp[i-1][j-1]
b := dp[i-1][j]
if b < a {
a = b
}
dp[i][j] = a + tri[i][j]
}
}
}
ans := dp[n-1][0]
for j := 1; j < len(dp[n-1]); j++ {
if dp[n-1][j] < ans {
ans = dp[n-1][j]
}
}
return ans
}

func main() {
fmt.Println(minPath([][]int{{2}, {3, 4}, {6, 5, 7}, {4, 1, 8, 3}}))
fmt.Println(minPath([][]int{{-1}, {2, 3}, {1, -1, -3}}))
fmt.Println(minPath([][]int{{5}, {6, 7}}))
}
