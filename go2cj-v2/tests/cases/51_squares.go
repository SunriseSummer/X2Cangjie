package main

import "fmt"

func square(x int) int {
	return x * x
}

func main() {
	for i := 1; i <= 5; i++ {
		fmt.Println(square(i))
	}
}
