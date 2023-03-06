<h1 align="center">
  <br>
  <a href="https://github.com/Tzion0/Cupid"><img src="https://github.com/Tzion0/Cupid/blob/main/cupid-logo.jpg" alt="Cupid"></a>
  <br>
  Cupid
  <br>
</h1>

Cupid, a python script that send random HTTP traffic with love, specifically designed for Attack & Defense (A&D) Competition.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

Detailed instructions on how to install the project and its dependencies.
```
git clone <URL>
cd cupid
pip3 install -r requirements.txt
```

## Usage

Run the script
```
python cupid.py -c config.json
```
View other command-line arguments
```
$ python cupid.py -h
usage: cupid.py [-h] -c <file_path> [-p] [-l] [-t] [-s]

options:
  -h, --help            show this help message and exit
  -c <file_path>, --config <file_path>
                        Path to config file (e.g. examples/config.json)
  -p , --payload        Payload to simulate the payload traffic by generate wordlist from it
  -l , --log            Logging level (e.g. "info"/"debug")
  -t , --timeout        Duration of traffic should be send, in seconds (e.g. 180)
  -s , --sleep          Sleep after every round of traffic sent, in seconds (e.g. 1)
```

## Notes

- The config file should contain all configuration information; command-line arguments are merely for convenience
- Command-line parameters are given precedence over configuration files and will take precedence
- The key (option) name ends with `_file` in config file will override the value of key (option) name without `_file`

    ```
    E.g. user_agents_file will override user_agents option's value 
    ```
- See [examples/full_config.json](examples/full_config.json) to obtain the configuration file's complete list of available key (option). 

## Acknowledgements

This project has been inspired by
* [Noisy](https://github.com/1tayH/noisy/)

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details
