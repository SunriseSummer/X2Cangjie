package main

import "fmt"

func minCoins(coins []int, target int) int {
const INF = 1 << 30
dp := make([]int, target+1)
for i := 1; i <= target; i++ {
dp[i] = INF
}
for i := 1; i <= target; i++ {
for _, c := range coins {
if c <= i && dp[i-c]+1 < dp[i] {
dp[i] = dp[i-c] + 1
}
}
}
if dp[target] >= INF {
return -1
}
return dp[target]
}

func main() {
fmt.Println(minCoins([]int{1, 2, 5}, 11))
fmt.Println(minCoins([]int{2}, 3))
fmt.Println(minCoins([]int{2, 4, 6}, 8))
}
