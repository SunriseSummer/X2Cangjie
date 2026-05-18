package main

import "fmt"

func minCost(cost []int) int {
n := len(cost)
if n == 0 {
return 0
}
if n == 1 {
return cost[0]
}
dp := make([]int, n)
dp[0] = cost[0]
if cost[1] < cost[0] {
dp[1] = cost[1]
} else {
dp[1] = cost[0]
}
for i := 2; i < n; i++ {
if dp[i-1] < dp[i-2] {
dp[i] = cost[i] + dp[i-1]
} else {
dp[i] = cost[i] + dp[i-2]
}
}
if dp[n-1] < dp[n-2] {
return dp[n-1]
}
return dp[n-2]
}

func main() {
fmt.Println(minCost([]int{10, 15, 20}))
fmt.Println(minCost([]int{1, 100, 1, 1, 1, 100, 1, 1, 100, 1}))
fmt.Println(minCost([]int{0, 0, 0, 1}))
}
