package cmd

import (
	"os"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var rootCmd = &cobra.Command{
	Use:   "testbench",
	Short: "Agent Testbench CLI — record AI agent test run results",
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func init() {
	viper.SetEnvPrefix("TESTBENCH")
	viper.AutomaticEnv()

	// TESTBENCH_API_URL overrides the default; flag overrides the env var.
	rootCmd.PersistentFlags().String("api-url", "http://localhost:5000", "Testbench API base URL")
	viper.BindPFlag("api_url", rootCmd.PersistentFlags().Lookup("api-url"))
}
