package main

import "fmt"

func sieve(n int) []int {
	mark := make([]int, n+1)
	for i := 2; i <= n; i++ {
		if mark[i] == 0 {
			for j := i * i; j <= n; j = j + i {
				mark[j] = 1
			}
		}
	}
	primes := []int{}
	for i := 2; i <= n; i++ {
		if mark[i] == 0 {
			primes = append(primes, i)
		}
	}
	return primes
}

func main() {
	ps := sieve(30)
	for _, p := range ps {
		fmt.Println(p)
	}
}
