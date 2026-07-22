package main

import "fmt"

func ways(amount int, coins []int) int {
dp := make([]int, amount+1)
dp[0] = 1
for i := 0; i < len(coins); i++ {
c := coins[i]
for v := c; v <= amount; v++ {
dp[v] += dp[v-c]
}
}
return dp[amount]
}

func main() {
fmt.Println(ways(5, []int{1, 2, 5}))
fmt.Println(ways(3, []int{2}))
fmt.Println(ways(10, []int{2, 5, 3, 6}))
}
