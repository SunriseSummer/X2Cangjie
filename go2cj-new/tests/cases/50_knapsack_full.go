package main

import "fmt"

// Helper: integer maximum.
func max(a int, b int) int {
	if a > b {
		return a
	}
	return b
}

// Helper: integer minimum.
func min(a int, b int) int {
	if a < b {
		return a
	}
	return b
}

// Classic 01 knapsack DP with a 1-D rolling array.
// Returns the maximum value achievable with the given capacity.
func knapsack01(weights []int, values []int, capacity int) int {
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

// Unbounded knapsack: each item can be taken any number of times.
func knapsackUnbounded(weights []int, values []int, capacity int) int {
	n := len(weights)
	dp := make([]int, capacity+1)
	for i := 0; i < n; i++ {
		for w := weights[i]; w <= capacity; w++ {
			dp[w] = max(dp[w], dp[w-weights[i]]+values[i])
		}
	}
	return dp[capacity]
}

// Reports the total weight chosen by a greedy heuristic — strictly
// less optimal than the DP solution; included to test the gap between
// the two approaches in this end-to-end translation suite.
func greedyValue(weights []int, values []int, capacity int) int {
	n := len(weights)
	total := 0
	remaining := capacity
	for i := 0; i < n; i++ {
		if weights[i] <= remaining {
			total += values[i]
			remaining -= weights[i]
		}
	}
	return total
}

func main() {
	weights := []int{2, 3, 4, 5}
	values := []int{3, 4, 5, 6}
	capacity := 8
	fmt.Println(knapsack01(weights, values, capacity))
	fmt.Println(knapsackUnbounded(weights, values, capacity))
	fmt.Println(greedyValue(weights, values, capacity))
	fmt.Println(min(3, 7))
	fmt.Println(max(10, 4))
}
