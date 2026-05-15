package main

import "fmt"

func main() {
	matrix := [][]int{
		{1, 2, 3},
		{4, 5, 6},
		{7, 8, 9},
	}
	total := 0
	for _, row := range matrix {
		for _, v := range row {
			total += v
		}
	}
	fmt.Println(total)
}
