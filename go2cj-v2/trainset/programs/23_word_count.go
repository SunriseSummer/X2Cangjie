package main

import "fmt"

func countWords(s string) int {
	if len(s) == 0 {
		return 0
	}
	count := 0
	inWord := false
	for i := 0; i < len(s); i++ {
		if s[i] == ' ' {
			inWord = false
		} else if !inWord {
			inWord = true
			count++
		}
	}
	return count
}

func main() {
	fmt.Println(countWords("hello world"))
	fmt.Println(countWords("one two three four"))
	fmt.Println(countWords(""))
	fmt.Println(countWords("single"))
}
