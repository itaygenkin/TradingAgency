### Pre-requisites:
1. Python 3.10 or higher
2. `pip install pytest pytest-asyncio`

### How to run unit tests:
- Run specific file: `pytest .\tests\unit_tests\<test_file> -v -s`
- Run specific class: `pytest .\tests\unit_tests\<test_file>::<test_class> -v -s`
- Run specific test: `pytest .\tests\unit_tests\<test_file>::<test_class>::<test_method> -v -s`
- Optional: `-v` for verbose output, `-s` to disable output capturing.

### How to run integration tests:
1. `docker run -p 6379:6379 -d redis`
2. `pytest .\tests\integration_tests\<test_file>::<test_class> -v -s`
