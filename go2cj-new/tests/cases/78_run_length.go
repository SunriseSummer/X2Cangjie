package main

import "fmt"

func runLengthCount(xs []int) int {
	if len(xs) == 0 {
		return 0
	}
	runs := 1
	for i := 1; i < len(xs); i++ {
		if xs[i] != xs[i-1] {
			runs = runs + 1
		}
	}
	return runs
}

func main() {
	xs := []int{1, 1, 2, 2, 2, 3, 1, 1}
	fmt.Println(runLengthCount(xs))
	ys := []int{7, 7, 7, 7}
	fmt.Println(runLengthCount(ys))
	zs := []int{1, 2, 3, 4, 5}
	fmt.Println(runLengthCount(zs))
}
