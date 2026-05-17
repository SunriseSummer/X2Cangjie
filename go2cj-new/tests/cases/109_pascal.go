package main

import "fmt"

func pascal(rows int) [][]int {
	t := make([][]int, rows)
	for i := 0; i < rows; i++ {
		t[i] = make([]int, i+1)
		t[i][0] = 1
		t[i][i] = 1
		for j := 1; j < i; j++ {
			t[i][j] = t[i-1][j-1] + t[i-1][j]
		}
	}
	return t
}

func main() {
	tri := pascal(5)
	for i := 0; i < 5; i++ {
		for j := 0; j <= i; j++ {
			fmt.Println(tri[i][j])
		}
	}
}
