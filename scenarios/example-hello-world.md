---
name: hello-world
category: coding
difficulty: easy
type: model
description: Baseline prompt to verify the model responds and produces runnable code
tags: [baseline, python, smoke]
suite: baseline-suite
grading_criteria: |
  The response must define a Python function named `greet` that accepts a single
  string argument and returns a string of the form "Hello, {name}!". The function
  must include a docstring. Award full marks if the implementation is correct and
  includes a docstring; partial if the logic is correct but the docstring is
  missing; fail if the function name, signature, or return value is wrong.
---

Write a Python function called `greet(name: str) -> str` that returns `"Hello, {name}!"`. Include a brief docstring. No imports needed.
