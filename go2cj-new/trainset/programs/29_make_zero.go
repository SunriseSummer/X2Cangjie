package main

import "fmt"

func main() {
	n := 5
	dp := make([]int, n)
	for i := 0; i < n; i++ {
		dp[i] = i * i
	}
	for i := 0; i < n; i++ {
		fmt.Println(dp[i])
	}
}
