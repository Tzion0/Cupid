import argparse, requests, json, random, threading, hashlib, datetime, time, re, string, logging
from urllib.parse import urlparse, urljoin

# MUST include these key (option) in config file
OPTIONS_REQUIRED = ["user_agents", "urls"]

class Arrow:
    def __init__(self, co):
        """
        Arrow (data) class initialization
        """
        self._config = {}

    class OptionRequiredNotFound(Exception):
        """
        Raised when the required option key in config file not found
        """
        pass

    @staticmethod
    def _is_valid_url(url):
        """
        Check if a url is a valid url.
        :param url: url to be checked
        :return: raise ValueError if the url is not valid
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


    def _gen_fake_flag(self):
        """
        Generate bunch of fake flags for POST request data (post_request_data) later, therefore we don't have to add it manually in config file
        Default number of fake flags: 50
        """
        for i in range(50):
            self._config["post_request_data"].append({"flag":self._config["flag_format"] if "flag_format" in self._config else "FLAG" + "{" + hashlib.md5(f"{random.randint(i,i+50)}".encode('utf-8')).hexdigest() + "}"})

    def _set_option_default_value(self):
        """
        Ensure certain config options has value, else set to None or []
        """
        if "post_request_data" not in self._config:
            self.set_option("post_request_data", [])
        if "request_dir" not in self._config:
            self.set_option("request_dir", [])

    def _config_value_check(self):
        self._set_option_default_value()

        """
        Check if minimum required options are found
        """
        for option in OPTIONS_REQUIRED:
            if option not in self._config:
                raise self.OptionRequiredNotFound(f"Config file does not contains minimum required options (key) : [{', '.join(OPTIONS_REQUIRED)}]")

        """
        Validate URL format
        """
        for url in self._config["urls"]:
            if not self._is_valid_url(url):
                raise ValueError(f"Invalid URL '{url}'")
            
        """
        Extract words from payload and add into request_dir wordlist
        """
        if "payload" in self._config:
            if isinstance(self._config["payload"], list):
                for p in self._config["payload"]:
                    words = re.sub('['+string.punctuation.replace(".","")+']', ' ', p).split()
            else:
                words = re.sub('['+string.punctuation.replace(".","")+']', ' ', self._config["payload"]).split()
            
            for word in words:
                self._config["request_dir"].append(word)

    def load_config(self, file_path):
        """
        Load and set based on config file. Ensure all config options has value, else set to None or [] for specific option
        :param file_path: config file path (e.g. examples/config.json)
        """
        with open(file_path, "r") as config_file:
            config = json.load(config_file)

        self._config = config
        
        """
        Override/Set new option with file contents of option value contains file path
        """
        for option in self._config:
            if option.endswith("_file"):
                with open(self._config[option], "r") as f:
                    self.set_option(option[:-5], f.read().strip().split("\n"))

        self._config_value_check()
        self._gen_fake_flag()

    def set_option(self, option, value):
        """
        Set option separately
        :param option: config file json key
        :param value: config file json key's value
        """
        self._config[option] = value

class Cupid:
    def __init__(self, arrowObj):
        """
        Cupid class initialization
        """
        self._config = arrowObj._config
        self._start_time = None

    def _request_get(self, url):
        """
        Send GET request to URL specified with random user agent
        """
        random_user_agent = random.choice(self._config["user_agents"])
        url = urljoin(url, random.choice(self._config["request_dir"]) if self._config["request_dir"] else None)
        response = requests.get(url, headers={'user-agent': random_user_agent}, timeout=5)
        return response
    
    def _request_post(self, url):
        """
        Send POST request to URL specified with random user agent.
        The data sent will be random of flag (useful for A&D)
        """
        random_user_agent = random.choice(self._config["user_agents"])
        data = random.choice(self._config["post_request_data"])
        url = urljoin(url, random.choice(self._config["request_dir"]) if self._config["request_dir"] else None)
        response = requests.post(url, headers={'user-agent': random_user_agent}, data=data, timeout=5)
        return response
    
    class CupidTimedOut(Exception):
        """
        Raised when the specified timeout is exceeded
        """
        pass
    
    def _is_timeout_reached(self):
        """
        Determines whether the specified timeout has reached, raise the exception is reached
        """
        end_time = self._start_time + datetime.timedelta(seconds=int(self._config["timeout"]))
        if datetime.datetime.now() >= end_time:
            raise self.CupidTimedOut

    def sendLove(self):
        self._start_time = datetime.datetime.now()

        """
        Utilize threading for sending GET & POST request to each URLs
        """
        while True:
            threads = []
            get_responses = []
            post_responses = []

            try:
                for url in self._config["urls"]:
                    thread1 = threading.Thread(target=lambda url: get_responses.append(self._request_get(url)), args=(url,))
                    thread2 = threading.Thread(target=lambda url: post_responses.append(self._request_post(url)), args=(url,))
                    threads.append(thread1)
                    threads.append(thread2)
                    thread1.start()
                    thread2.start()
                    
                for thread in threads:
                    thread.join()

                # Check timeout reached or not
                if "timeout" in self._config:
                    self._is_timeout_reached()

                # Request send every few second(s). Default: 1 or 2 seconds
                time.sleep(int(self._config["sleep"]) if "sleep" in self._config else random.randint(1,2))

                # Log the responses
                for r in get_responses:
                    logging.info(f"[GET] {r.url} {r.status_code}")
                for r in post_responses:
                    logging.info(f"[POST] {r.url} {r.status_code} : {r.request.body}")

            except Exception as e:
                logging.warning(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', metavar='<file_path>', required=True, type=str, help='Path to config file (e.g. examples/config.json)', default=False)
    parser.add_argument('-p', '--payload', metavar='', required=False, type=str, help='Payload to simulate the payload traffic by generate wordlist from it', default=False)
    parser.add_argument('-l', '--log', metavar='', dest='update',required=False, type=str, help='Logging level (e.g. "info"/"debug")')
    parser.add_argument('-t', '--timeout', metavar='', required=False, type=int, help='Duration of traffic should be send, in seconds (e.g. 180)', default=False)
    parser.add_argument('-s', '--sleep', metavar='', required=False, type=int, help='Sleep after every round of traffic sent, in seconds (e.g. 1)', default=False)
    args = parser.parse_args()

    """
    Load and set based on config file provided
    Notes:
    1. Any other argument provided will override the one in config file
    2. Option in config file ends with '_file' will override the option does not ends with '_file' 
    """
    arrow = Arrow(args.config)
    arrow.load_config(args.config)

    """
    Explicitly set command-line provided arguments
    """
    args_dict = vars(args)
    for key, value in args_dict.items():
        if key == "timeout" and value:
            print(key, value)
            arrow.set_option(key, value)
        elif key == "payload" and value:
            arrow.set_option(key, value)
        elif key == "sleep" and value:
            arrow.set_option(key, value)
        elif key == "log" and value:
            level = getattr(logging, args.log.upper())
            logging.basicConfig(level=level)

    """
    Equip arrow (data) on cupid
    """
    cupid = Cupid(arrow)
    cupid.sendLove()

if __name__ == '__main__':
    main()