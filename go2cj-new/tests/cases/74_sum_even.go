package main

import "fmt"

func sumEven(n int) int {
	s := 0
	for i := 2; i <= n; i = i + 2 {
		s = s + i
	}
	return s
}

func main() {
	fmt.Println(sumEven(0))
	fmt.Println(sumEven(10))
	fmt.Println(sumEven(20))
}
