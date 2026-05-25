BINARY    := testbench
BUILD_DIR := builds
MODULE    := github.com/awesomejt/agent-testbench/cli

.PHONY: build build-linux test lint clean

build:
	mkdir -p $(BUILD_DIR)
	go build -o $(BUILD_DIR)/$(BINARY) .

# Cross-compile for Linux amd64 (deploy target: test VMs)
build-linux:
	mkdir -p $(BUILD_DIR)
	GOOS=linux GOARCH=amd64 go build -o $(BUILD_DIR)/$(BINARY)-linux-amd64 .

test:
	go test ./... -v

lint:
	go vet ./...

clean:
	rm -rf $(BUILD_DIR)
