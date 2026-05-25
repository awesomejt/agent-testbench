package client_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/awesomejt/agent-testbench/cli/internal/client"
)

func TestCreateRun(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost || r.URL.Path != "/runs/" {
			t.Errorf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]any{"id": 1})
	}))
	defer srv.Close()

	c := client.New(srv.URL)
	result, err := c.CreateRun(map[string]any{"run_name": "smoke", "scenario_name": "hello-world"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result["id"] == nil {
		t.Error("expected id in response")
	}
}

func TestCreateRun_APIError(t *testing.T) {
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
