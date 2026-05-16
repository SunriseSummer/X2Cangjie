package main

import "fmt"

func countPrimes(limit int) int {
	if limit < 2 {
		return 0
	}
	sieve := make([]int, limit+1)
	for i := 2; i*i <= limit; i++ {
		if sieve[i] == 0 {
			for j := i * i; j <= limit; j = j + i {
				sieve[j] = 1
			}
		}
	}
	c := 0
	for i := 2; i <= limit; i++ {
		if sieve[i] == 0 {
			c = c + 1
		}
	}
	return c
}

func main() {
	fmt.Println(countPrimes(10))
	fmt.Println(countPrimes(100))
	fmt.Println(countPrimes(1))
}
