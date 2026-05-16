package main

import "fmt"

func main() {
	matrix := [][]int{
		{1, 2, 3},
		{4, 5, 6},
	}
	for _, row := range matrix {
		sum := 0
		for _, v := range row {
			sum += v
		}
		fmt.Println(sum)
	}
}
