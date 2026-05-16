package main

import "fmt"

func sumUpTo(n int) int {
	s := 0
	i := 1
	for i <= n {
		s = s + i
		i = i + 1
	}
	return s
}

func main() {
	fmt.Println(sumUpTo(0))
	fmt.Println(sumUpTo(5))
	fmt.Println(sumUpTo(100))
}
