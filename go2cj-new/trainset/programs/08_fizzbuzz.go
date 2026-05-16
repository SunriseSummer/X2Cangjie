package main

import "fmt"

func main() {
	for n := 1; n <= 15; n++ {
		if n%15 == 0 {
			fmt.Println("FizzBuzz")
		} else if n%3 == 0 {
			fmt.Println("Fizz")
		} else if n%5 == 0 {
			fmt.Println("Buzz")
		} else {
			fmt.Println(n)
		}
	}
}
