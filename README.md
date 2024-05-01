# Project
The main code base for the project

# Install

1. Make a virtual environment
```bash 
python -m venv .venv/
```
2. Activate the virtual environment
```bash
source .venv/bin/activate
```
3. Install the required libraries
```bash
pip install -r requirements.txt
```
4. Run setuptools
```bash
pip install -e .
```

# Modify Requirements

If you install a new package in the virtual environment and you want it to be a permanent part of the repository then make sure to add it to the `requirements.txt`.
You can do this with the following command
```bash
pip freeze > requirements.txt
```

# Postgresql
Make sure you have a postgresql server running on localhost.
If you are getting authentication failure then check that password and user matches
[Check this stackoverflow post to debug](https://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge)
## Fresh db
To run the application with a fresh database, `python main.py --fresh-db`

# Benchmarking
Benchmarking is an addition to Pytest, meaning it is only used in context of Pytest tests.
To use it include it as a fixture to you test as:
```python
def test_myfunc(benchmark):
    benchmark(myfunc)
```
If we have a function such as:
```python
def myfunc(num, str):
    #... some code

def test_myfunc(benchmark):
    benchmark(myfunc, kwargs={'num':1, 'str':'hello'})
```
Usually benchmark runs 5 rounds of 10 iterations, meaning 50 runs, this is excessive for our need, to define it we can do the following:
```python
def test_benchmark_pendatic(benchmark):
    benchmark.pedantic(myfunc, rounds=1, iterations=1, warmup_rounds=0)
```
## Custom marks
To ensure that benchmarks do not run together with other tests we use the following marks:
bm_cheap, bm_mid, bm_expensive, which are used as markers in pytest:
```python
@pytest.mark.bm_cheap
def test_myfunc(benchmark):
    #... some test
```
They are included on a per test basis. To run use the follwoing commands when calling pytest:
--benchmark-cheap (cheap) or
--benchmark-mid (mid) or
--benchmark (expensive)