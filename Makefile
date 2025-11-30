help: ## Show this help message
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

clean: clean_output ## Clean all
 
###############################################################################

pytest: ## Run pytest on the tests/ directory
	cd tests && pytest -W ignore::DeprecationWarning

pytest_verbose: ## Run pytest in verbose mode on the tests/ directory
	cd tests && pytest -v -W ignore::DeprecationWarning

run_all_examples: ## Run all examples to ensure they work
	python3 ./tools/run_all_examples.py

check_expected_output: ## Check the output files against expected files
	python3 ./tools/check_expected_output.py

clean_output: ## Clean all generated output files png,json,pdf,svg
	rm -f ./examples/output/*.{png,json,pdf,svg}

##############################################################################

lint: ## Run pyright type checker on src and examples
	pyright ./src/gsp/ ./src/gsp_matplotlib/ ./src/gsp_datoviz/ ./src/gsp_pydantic/ ./src/gsp_nico/ ./examples/ 

test: lint pytest_verbose run_all_examples check_expected_output ## Run all tests
	@echo "All tests passed!"

###############################################################################

stubs_clean: ## Remove all generated type stubs
	rm -rf ./stubs/gsp

stubs_gsp: stubs_clean ## Generate type stubs for src/gsp
	stubgen -p gsp -o ./stubs/
	stubgen -p gsp_matplotlib -o ./stubs/

###############################################################################

network_server_dev: network_server_kill ## Run the network server in development mode
	watchmedo auto-restart -d ./src -d ./tools -p="*.py" -R  -- python ./src/gsp_network/tools/network_server.py

network_server_kill: ## Kill any process using port 5000 (commonly used for network servers)
	python3 ./src/gsp_network/tools/network_server_kill.py
	
network_server: ## Run the network renderer server
	python3 ./src/gsp_network/tools/network_server.py