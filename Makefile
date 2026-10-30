PY ?= python

env:
	$(PY) -m pip install -r requirements.txt

data:
	$(PY) -m src.data_gen.generate --config configs/data.yaml --all

test:
	$(PY) -m pytest -q

smoke:
	$(PY) -m src.baselines.run_all --split smoke --methods greedy,lawnmower,ortools_1s,ortools_5s,ortools_30s

baselines:
	$(PY) -m src.baselines.run_all --split small_test --methods all
	$(PY) -m src.baselines.run_all --split test --methods all
	$(PY) -m src.baselines.run_all --split test_small_n --methods all

tables:
	$(PY) -m src.eval.benchmark --all
	$(PY) -m src.eval.plots --split small_test
	$(PY) -m src.eval.plots --split test
	$(PY) -m src.eval.plots --split test_small_n

all: data test baselines tables

.PHONY: env data test smoke baselines tables all
