package main

import "fmt"

func matMul(a [][]int, b [][]int, n int) [][]int {
	c := make([][]int, n)
	for i := 0; i < n; i++ {
		c[i] = make([]int, n)
	}
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			s := 0
			for k := 0; k < n; k++ {
				s = s + a[i][k]*b[k][j]
			}
			c[i][j] = s
		}
	}
	return c
}

func main() {
	a := [][]int{{1, 2}, {3, 4}}
	b := [][]int{{5, 6}, {7, 8}}
	c := matMul(a, b, 2)
	for i := 0; i < 2; i++ {
		fmt.Println(c[i][0], c[i][1])
	}
}
