package main

import "fmt"

func main() {
	xs := []int{1, 2, 3, 4, 5}
	total := 0
	for _, x := range xs {
		total += x
	}
	fmt.Println(total)
}
