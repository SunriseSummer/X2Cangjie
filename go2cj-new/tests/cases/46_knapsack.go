package main

import "fmt"

func max(a int, b int) int {
	if a > b {
		return a
	}
	return b
}

func knapsack(weights []int, values []int, capacity int) int {
	n := len(weights)
	dp := make([]int, capacity+1)
	for i := 0; i < n; i++ {
		w := capacity
		for w >= weights[i] {
			dp[w] = max(dp[w], dp[w-weights[i]]+values[i])
			w--
		}
	}
	return dp[capacity]
}

func main() {
	weights := []int{1, 3, 4, 5}
	values := []int{1, 4, 5, 7}
	fmt.Println(knapsack(weights, values, 7))
}
