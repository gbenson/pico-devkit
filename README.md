# pico-devkit

MicroPython development environment.

## Setup

```sh
git clone https://github.com/gbenson/pico-devkit.git
cd pico-devkit
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
make check
```
