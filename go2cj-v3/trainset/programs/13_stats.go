package main

import "fmt"

func main() {
	xs := []int{3, 1, 4, 1, 5, 9, 2, 6}
	maxVal := xs[0]
	minVal := xs[0]
	sum := 0
	for _, x := range xs {
		if x > maxVal {
			maxVal = x
		}
		if x < minVal {
			minVal = x
		}
		sum += x
	}
	fmt.Println(maxVal)
	fmt.Println(minVal)
	fmt.Println(sum)
}
