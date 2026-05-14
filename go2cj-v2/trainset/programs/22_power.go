package main

import "fmt"

func power(base, exp int) int {
	if exp == 0 {
		return 1
	}
	if exp%2 == 0 {
		half := power(base, exp/2)
		return half * half
	}
	return base * power(base, exp-1)
}

func main() {
	fmt.Println(power(2, 10))
	fmt.Println(power(3, 4))
	fmt.Println(power(5, 0))
	fmt.Println(power(7, 1))
}
