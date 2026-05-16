package main

import "fmt"

func transpose(m [][]int, rows int, cols int) [][]int {
	t := make([][]int, cols)
	for i := 0; i < cols; i++ {
		t[i] = make([]int, rows)
	}
	for i := 0; i < rows; i++ {
		for j := 0; j < cols; j++ {
			t[j][i] = m[i][j]
		}
	}
	return t
}

func main() {
	m := [][]int{{1, 2, 3}, {4, 5, 6}}
	t := transpose(m, 2, 3)
	for i := 0; i < 3; i++ {
		fmt.Println(t[i][0], t[i][1])
	}
}
