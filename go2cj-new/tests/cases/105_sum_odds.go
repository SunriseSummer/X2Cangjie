package main

import "fmt"

func sumOdds(n int) int {
	s := 0
	for i := 1; i <= n; i = i + 2 {
		s = s + i
	}
	return s
}

func main() {
	fmt.Println(sumOdds(1))
	fmt.Println(sumOdds(9))
	fmt.Println(sumOdds(20))
}
