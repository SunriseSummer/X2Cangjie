package main

import "fmt"

func countOccurrences(xs []int, target int) int {
	c := 0
	for _, v := range xs {
		if v == target {
			c = c + 1
		}
	}
	return c
}

func main() {
	xs := []int{1, 2, 3, 2, 4, 2, 5, 2}
	fmt.Println(countOccurrences(xs, 2))
	fmt.Println(countOccurrences(xs, 7))
	fmt.Println(countOccurrences(xs, 1))
}
