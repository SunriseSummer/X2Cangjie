package main

import "fmt"

func min(a, b int) int {
if a < b {
return a
}
return b
}

func editDistance(s, t string) int {
n := len(s)
m := len(t)
dp := make([][]int, n+1)
for i := 0; i <= n; i++ {
dp[i] = make([]int, m+1)
}
for i := 0; i <= n; i++ {
dp[i][0] = i
}
for j := 0; j <= m; j++ {
dp[0][j] = j
}
for i := 1; i <= n; i++ {
for j := 1; j <= m; j++ {
if s[i-1] == t[j-1] {
dp[i][j] = dp[i-1][j-1]
} else {
dp[i][j] = min(dp[i-1][j], min(dp[i][j-1], dp[i-1][j-1])) + 1
}
}
}
return dp[n][m]
}

func main() {
fmt.Println(editDistance("kitten", "sitting"))
fmt.Println(editDistance("flaw", "lawn"))
fmt.Println(editDistance("abc", "abc"))
}
