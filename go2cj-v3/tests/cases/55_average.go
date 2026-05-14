package main

import "fmt"

func main() {
	xs := []int{10, 20, 30, 40, 50}
	total := 0
	for _, v := range xs {
		total += v
	}
	fmt.Println(total)
	fmt.Println(total / len(xs))
}
