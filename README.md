# selenium-v-requests-comparison
A small library that compares the timing results between Selenium and HTML requests.

## Installation

Clone the repository:
```
git clone https://github.com/joseph-c-mcguire/selenium-v-requests-comparison.git
cd selenium-v-requests-comparison
```

Install the package using pip:
```
pip install .
```

## Usage

Run the comparison tool from the command line:
```
selenium_v_requests_comparison [--debug]
```
The `--debug` flag enables debug logging for more detailed output.

When run, the tool:
- Verifies that Google Chrome is installed.
- Executes a series of performance tests using both the requests library and Selenium for a given URL.
- Generates and saves a boxplot of the timing results as `comparison_boxplot.png`.

## Configuration

- Ensure that Google Chrome is installed on your system.
- You can adjust the number of experiments by updating the `EXPERIMENT_COUNT` variable in `comparison.py`.

## License

MIT License. See the LICENSE file for details.
