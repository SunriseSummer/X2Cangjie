package main

import "fmt"

func wordBreak(s string, dict []string) bool {
set := map[string]bool{}
for _, w := range dict {
set[w] = true
}
n := len(s)
dp := make([]bool, n+1)
dp[0] = true
for i := 1; i <= n; i++ {
for j := 0; j < i; j++ {
if dp[j] && set[s[j:i]] {
dp[i] = true
break
}
}
}
return dp[n]
}

func main() {
fmt.Println(wordBreak("leetcode", []string{"leet", "code"}))
fmt.Println(wordBreak("applepenapple", []string{"apple", "pen"}))
fmt.Println(wordBreak("catsandog", []string{"cats", "dog", "sand", "and", "cat"}))
}
