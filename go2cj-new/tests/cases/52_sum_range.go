package main

import "fmt"

func sumTo(n int) int {
	s := 0
	for i := 1; i <= n; i++ {
		s = s + i
	}
	return s
}

func main() {
	fmt.Println(sumTo(10))
	fmt.Println(sumTo(100))
}
