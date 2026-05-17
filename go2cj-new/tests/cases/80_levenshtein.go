package main

import "fmt"

func levenshtein(a string, b string, m int, n int) int {
	dp := make([][]int, m+1)
	for i := 0; i <= m; i++ {
		dp[i] = make([]int, n+1)
	}
	for i := 0; i <= m; i++ {
		dp[i][0] = i
	}
	for j := 0; j <= n; j++ {
		dp[0][j] = j
	}
	for i := 1; i <= m; i++ {
		for j := 1; j <= n; j++ {
			cost := 1
			if a[i-1] == b[j-1] {
				cost = 0
			}
			d1 := dp[i-1][j] + 1
			d2 := dp[i][j-1] + 1
			d3 := dp[i-1][j-1] + cost
			m1 := d1
			if d2 < m1 {
				m1 = d2
			}
			if d3 < m1 {
				m1 = d3
			}
			dp[i][j] = m1
		}
	}
	return dp[m][n]
}

func main() {
	fmt.Println(levenshtein("kitten", "sitting", 6, 7))
	fmt.Println(levenshtein("flaw", "lawn", 4, 4))
	fmt.Println(levenshtein("abc", "abc", 3, 3))
}
