package main

import "fmt"

func isEven(n int) bool {
	return n%2 == 0
}

func main() {
	for i := 1; i <= 6; i++ {
		if isEven(i) {
			fmt.Println(i, "even")
		} else {
			fmt.Println(i, "odd")
		}
	}
}
