package main

import "fmt"

func factorial(n int) int {
	result := 1
	for i := 2; i <= n; i++ {
		result = result * i
	}
	return result
}

func main() {
	for i := 0; i <= 6; i++ {
		fmt.Println(i, factorial(i))
	}
}
