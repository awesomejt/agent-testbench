package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"

	"github.com/awesomejt/agent-testbench/cli/internal/client"
)

var recordCmd = &cobra.Command{
	Use:   "record",
	Short: "Post a run result to the API",
	RunE:  runRecord,
}

func init() {
	rootCmd.AddCommand(recordCmd)

	f := recordCmd.Flags()
	f.String("run-name", "", "Human-readable run label (required)")
	f.String("scenario", "", "Scenario name (required)")
	f.String("model", "", "Model name, e.g. claude-sonnet-4-6 (required)")
	f.String("provider", "", "Provider, e.g. anthropic, openai, local (required)")
	f.String("agent-server", "", "Local agent server, e.g. ollama, vllm (optional)")
	f.String("data", "", "Extra fields as a JSON string, or - to read from stdin")

	recordCmd.MarkFlagRequired("run-name")
	recordCmd.MarkFlagRequired("scenario")
	recordCmd.MarkFlagRequired("model")
	recordCmd.MarkFlagRequired("provider")
}

func runRecord(cmd *cobra.Command, _ []string) error {
	f := cmd.Flags()

	payload := map[string]any{
		"run_name":      must(f.GetString("run-name")),
		"scenario_name": must(f.GetString("scenario")),
		"model_name":    must(f.GetString("model")),
		"provider":      must(f.GetString("provider")),
	}

	if srv, _ := f.GetString("agent-server"); srv != "" {
		payload["agent_server"] = srv
	}

	dataFlag, _ := f.GetString("data")
	if dataFlag == "-" {
		var extra map[string]any
		if err := json.NewDecoder(os.Stdin).Decode(&extra); err != nil {
			return fmt.Errorf("reading stdin: %w", err)
		}
		for k, v := range extra {
			payload[k] = v
		}
	} else if dataFlag != "" {
		var extra map[string]any
		if err := json.Unmarshal([]byte(dataFlag), &extra); err != nil {
			return fmt.Errorf("parsing --data: %w", err)
		}
		for k, v := range extra {
			payload[k] = v
		}
	}

	c := client.New(viper.GetString("api_url"))
	result, err := c.CreateRun(payload)
	if err != nil {
		return err
	}

	out, _ := json.MarshalIndent(result, "", "  ")
	fmt.Println(string(out))
	return nil
}

func must[T any](v T, err error) T {
	if err != nil {
		panic(err)
	}
	return v
}
