package main

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

func main() {

	for i := 1; i < 60; i++ {
		var sleepTime int
		fmt.Println(os.Getenv("ENV_VAR1"), os.Getenv("ENV_VAR2"), i)
		sleepTime, _ = strconv.Atoi(os.Getenv("SLEEP_TIME"))
		if sleepTime == 0 {
			sleepTime = 1
		}
		time.Sleep(time.Duration(sleepTime) * time.Second)
	}
}
