package main

import "fmt"

func lis(xs []int) int {
	n := len(xs)
	if n == 0 {
		return 0
	}
	dp := make([]int, n)
	for i := 0; i < n; i++ {
		dp[i] = 1
	}
	for i := 1; i < n; i++ {
		for j := 0; j < i; j++ {
			if xs[j] < xs[i] {
				cand := dp[j] + 1
				if cand > dp[i] {
					dp[i] = cand
				}
			}
		}
	}
	best := dp[0]
	for i := 1; i < n; i++ {
		if dp[i] > best {
			best = dp[i]
		}
	}
	return best
}

func main() {
	xs := []int{10, 9, 2, 5, 3, 7, 101, 18}
	fmt.Println(lis(xs))
	ys := []int{0, 1, 0, 3, 2, 3}
	fmt.Println(lis(ys))
	zs := []int{7, 7, 7, 7}
	fmt.Println(lis(zs))
}
