package main

import "fmt"

func sumRange(lo, hi int) int {
	total := 0
	for i := lo; i <= hi; i++ {
		total += i
	}
	return total
}

func sumEven(lo, hi int) int {
	total := 0
	for i := lo; i <= hi; i++ {
		if i%2 == 0 {
			total += i
		}
	}
	return total
}

func main() {
	fmt.Println(sumRange(1, 100))
	fmt.Println(sumEven(1, 10))
	fmt.Println(sumRange(0, 0))
	fmt.Println(sumEven(2, 20))
}
