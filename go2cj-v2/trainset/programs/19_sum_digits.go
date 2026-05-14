package main

import "fmt"

func sumDigits(n int) int {
	total := 0
	for n > 0 {
		total += n % 10
		n /= 10
	}
	return total
}

func main() {
	fmt.Println(sumDigits(12345))
	fmt.Println(sumDigits(987654))
	fmt.Println(sumDigits(0))
	fmt.Println(sumDigits(7))
}
