package main

import "fmt"

func collatzSteps(n int) int {
	steps := 0
	for n > 1 {
		if n%2 == 0 {
			n = n / 2
		} else {
			n = 3*n + 1
		}
		steps = steps + 1
	}
	return steps
}

func main() {
	fmt.Println(collatzSteps(1))
	fmt.Println(collatzSteps(6))
	fmt.Println(collatzSteps(27))
}
