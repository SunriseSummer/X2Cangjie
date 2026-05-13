package main

import "fmt"

func fact(n int) int {
	if n <= 1 {
		return 1
	}
	return n * fact(n-1)
}

func main() {
	for i := 1; i <= 6; i++ {
		fmt.Println(fact(i))
	}
}
