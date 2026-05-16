package main

import "fmt"

func knapsack(weights []int, values []int, W int) int {
	n := len(weights)
	dp := make([][]int, n+1)
	for i := 0; i <= n; i++ {
		dp[i] = make([]int, W+1)
	}
	for i := 1; i <= n; i++ {
		for w := 0; w <= W; w++ {
			dp[i][w] = dp[i-1][w]
			if weights[i-1] <= w {
				cand := dp[i-1][w-weights[i-1]] + values[i-1]
				if cand > dp[i][w] {
					dp[i][w] = cand
				}
			}
		}
	}
	return dp[n][W]
}

func main() {
	w := []int{1, 3, 4, 5}
	v := []int{1, 4, 5, 7}
	fmt.Println(knapsack(w, v, 7))
	fmt.Println(knapsack(w, v, 3))
	fmt.Println(knapsack(w, v, 0))
}
