package main

import "fmt"

func sumTo(n int) int {
	total := 0
	for i := 1; i <= n; i++ {
		total += i
	}
	return total
}

func main() {
	fmt.Println(sumTo(10))
}
