package main

import "fmt"

func coinChange(coins []int, amount int) int {
	const INF = 1000000
	dp := make([]int, amount+1)
	for i := 1; i <= amount; i++ {
		dp[i] = INF
	}
	for i := 1; i <= amount; i++ {
		for _, c := range coins {
			if c <= i {
				cand := dp[i-c] + 1
				if cand < dp[i] {
					dp[i] = cand
				}
			}
		}
	}
	if dp[amount] >= INF {
		return -1
	}
	return dp[amount]
}

func main() {
	coins := []int{1, 2, 5}
	fmt.Println(coinChange(coins, 11))
	fmt.Println(coinChange(coins, 0))
	coins2 := []int{2}
	fmt.Println(coinChange(coins2, 3))
}
