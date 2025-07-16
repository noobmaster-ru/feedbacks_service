project_dir := .

.PHONY: reformat
reformat: ## Reformat code
	ruff format $(project_dir)
	ruff check $(project_dir) --fix