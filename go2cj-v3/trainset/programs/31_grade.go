package main

import "fmt"

func grade(s int) string {
	if s >= 90 {
		return "A"
	} else if s >= 80 {
		return "B"
	} else if s >= 70 {
		return "C"
	} else {
		return "F"
	}
}

func main() {
	fmt.Println(grade(91))
	fmt.Println(grade(82))
	fmt.Println(grade(73))
	fmt.Println(grade(60))
}
