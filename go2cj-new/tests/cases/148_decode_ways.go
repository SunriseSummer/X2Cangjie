package main

import "fmt"

func decodeWaysDigits(d []int) int {
	n := len(d)
	if n == 0 || d[0] == 0 {
		return 0
	}
	dp := make([]int, n+1)
	dp[0] = 1
	dp[1] = 1
	for i := 2; i <= n; i++ {
		if d[i-1] != 0 {
			dp[i] += dp[i-1]
		}
		two := d[i-2]*10 + d[i-1]
		if two >= 10 && two <= 26 {
			dp[i] += dp[i-2]
		}
	}
	return dp[n]
}

func main() {
	fmt.Println(decodeWaysDigits([]int{1, 2}))
	fmt.Println(decodeWaysDigits([]int{2, 2, 6}))
	fmt.Println(decodeWaysDigits([]int{1, 0, 0}))
}
