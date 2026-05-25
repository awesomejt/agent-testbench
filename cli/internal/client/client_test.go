package client_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/awesomejt/agent-testbench/cli/internal/client"
)

func TestCreateRun_Success(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Errorf("expected POST, got %s", r.Method)
		}
		if r.URL.Path != "/runs/" {
			t.Errorf("expected /runs/, got %s", r.URL.Path)
		}
		if ct := r.Header.Get("Content-Type"); ct != "application/json" {
			t.Errorf("expected application/json, got %s", ct)
		}
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]any{"id": 42, "run_name": "smoke"})
	}))
	defer srv.Close()

	c := client.New(srv.URL)
	result, err := c.CreateRun(map[string]any{"run_name": "smoke"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result["run_name"] != "smoke" {
		t.Errorf("expected run_name=smoke, got %v", result["run_name"])
	}
}

func TestCreateRun_ServerError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	}))
	defer srv.Close()

	c := client.New(srv.URL)
	_, err := c.CreateRun(map[string]any{})
	if err == nil {
		t.Error("expected error for 500 response")
	}
}

func TestCreateRun_BadGateway(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusBadGateway)
	}))
	defer srv.Close()

	c := client.New(srv.URL)
	_, err := c.CreateRun(map[string]any{})
	if err == nil {
		t.Error("expected error for 502 response")
	}
}

func TestCreateRun_ConnectionRefused(t *testing.T) {
	c := client.New("http://127.0.0.1:19999") // nothing listening
	_, err := c.CreateRun(map[string]any{})
	if err == nil {
		t.Error("expected error when server is unreachable")
	}
}

func TestCreateRun_Timeout(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(2 * time.Second) // longer than client timeout
	}))
	defer srv.Close()

	// Create a client with a very short timeout to trigger timeout error
	c := client.NewWithTimeout(srv.URL, 50*time.Millisecond)
	_, err := c.CreateRun(map[string]any{})
	if err == nil {
		t.Error("expected timeout error")
	}
}
