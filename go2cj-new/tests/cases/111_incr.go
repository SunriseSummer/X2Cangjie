package main

import "fmt"

func incr(x int) int {
	return x + 1
}

func main() {
	for i := 0; i < 4; i++ {
		fmt.Println(incr(i))
	}
}
