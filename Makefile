.PHONY: demo test eval clean

demo:
	docker-compose up --build -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Generating seed data..."
	python tools/seed/generate.py
	@echo "Demo started. UI available at http://localhost:5173"

clean:
	docker-compose down -v
	rm -rf data/state/* data/seed/* data/stream/*

test:
	pytest tests/unit

eval:
	python eval/run_accuracy.py

drill-crash:
	@echo "Simulating engine crash..."
	docker-compose kill -s SIGKILL engine
	@echo "Restarting engine..."
	docker-compose start engine
	@echo "Checking recovery..."
	# In a real scenario, we'd query the API to ensure no duplicates and state recovered
