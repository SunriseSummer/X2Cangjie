package main

import "fmt"

func sumOfSquares(n int) int {
	s := 0
	for i := 1; i <= n; i++ {
		s = s + i*i
	}
	return s
}

func main() {
	fmt.Println(sumOfSquares(0))
	fmt.Println(sumOfSquares(3))
	fmt.Println(sumOfSquares(10))
}
