package main

import "fmt"

func main() {
	xs := []int{4, 2, 7, 1, 5}
	maxVal := xs[0]
	for _, x := range xs {
		if x > maxVal {
			maxVal = x
		}
	}
	fmt.Println(maxVal)
}
