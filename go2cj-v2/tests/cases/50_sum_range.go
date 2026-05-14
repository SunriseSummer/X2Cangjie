package main

import "fmt"

func sumRange(lo, hi int) int {
	total := 0
	for i := lo; i <= hi; i++ {
		total += i
	}
	return total
}

func main() {
	fmt.Println(sumRange(1, 10))
	fmt.Println(sumRange(1, 100))
}
