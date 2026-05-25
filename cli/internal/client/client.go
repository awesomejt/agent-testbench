package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type Client struct {
	baseURL string
	http    *http.Client
}

func New(baseURL string) *Client {
	return NewWithTimeout(baseURL, 30*time.Second)
}

func NewWithTimeout(baseURL string, timeout time.Duration) *Client {
	return &Client{
		baseURL: baseURL,
		http:    &http.Client{Timeout: timeout},
	}
}

func (c *Client) CreateRun(payload map[string]any) (map[string]any, error) {
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	resp, err := c.http.Post(c.baseURL+"/runs/", "application/json", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("POST /runs/: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API returned %s", resp.Status)
	}

	var result map[string]any
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decoding response: %w", err)
	}
	return result, nil
}
