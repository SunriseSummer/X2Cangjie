package main

import "fmt"

func transpose2(m [][]int, r int, c int) [][]int {
	t := make([][]int, c)
	for i := 0; i < c; i++ {
		t[i] = make([]int, r)
	}
	for i := 0; i < r; i++ {
		for j := 0; j < c; j++ {
			t[j][i] = m[i][j]
		}
	}
	return t
}

func main() {
	m := [][]int{{1, 2, 3}, {4, 5, 6}}
	t := transpose2(m, 2, 3)
	for i := 0; i < 3; i++ {
		fmt.Println(t[i][0], t[i][1])
	}
}
