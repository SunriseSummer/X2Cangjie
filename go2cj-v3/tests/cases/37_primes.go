package main

import "fmt"

func isPrime(n int) bool {
	if n < 2 {
		return false
	}
	for i := 2; i*i <= n; i++ {
		if n%i == 0 {
			return false
		}
	}
	return true
}

func main() {
	for n := 2; n < 20; n++ {
		if isPrime(n) {
			fmt.Println(n)
		}
	}
}
