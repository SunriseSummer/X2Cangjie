package main

import "fmt"

func transpose(m [][]int) [][]int {
	rows := len(m)
	cols := len(m[0])
	out := make([][]int, cols)
	for i := 0; i < cols; i++ {
		out[i] = make([]int, rows)
	}
	for i := 0; i < rows; i++ {
		for j := 0; j < cols; j++ {
			out[j][i] = m[i][j]
		}
	}
	return out
}

func main() {
	m := [][]int{
		{1, 2, 3},
		{4, 5, 6},
	}
	t := transpose(m)
	for _, row := range t {
		for _, v := range row {
			fmt.Println(v)
		}
	}
}
