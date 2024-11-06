import os
import sys
import re
from pathlib import Path
import urllib.request
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
import tempfile
import zipfile
import subprocess

TRADING_TYPE = ["spot", "um", "cm"]
BASE_URL = 'https://data.binance.vision/'


def run_linux_command(command, cwd):
    try:
        process = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        exit_code = process.wait()
    except Exception as e:
        print(e)

    print(f'命令输出: {stdout.decode()}')
    print(f'退出码: {exit_code}')
    return stdout.decode()


def unzip_file(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        if len(file_list) == 1:
            extracted_path = zip_ref.extract(file_list[0])
        else:
            temp_dir = tempfile.mkdtemp()
            extracted_path = os.path.join(temp_dir, os.path.basename(zip_path)[:-4])
            os.mkdir(extracted_path)
            for file in file_list:
                zip_ref.extract(file, extracted_path)
            extracted_path = temp_dir
    return extracted_path


def get_destination_dir(file_url, folder=None):
    store_directory = os.environ.get('STORE_DIRECTORY')
    if folder:
        store_directory = folder
    if not store_directory:
        store_directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(store_directory, file_url)


def get_download_url(file_url):
    return "{}{}".format(BASE_URL, file_url)


def get_all_symbols(type, folder_end):
    # if type == 'um':
    #     response = urllib.request.urlopen("https://fapi.binance.com/fapi/v1/exchangeInfo").read()
    # elif type == 'cm':
    #     response = urllib.request.urlopen("https://dapi.binance.com/dapi/v1/exchangeInfo").read()
    # else:
    #     response = urllib.request.urlopen("https://api.binance.com/api/v3/exchangeInfo").read()
    #
    # result = list(map(lambda symbol: symbol['symbol'], json.loads(response)['symbols']))

    # 由于 API 秘钥的问题此处无法访问 API ...

    folder_list = ["BLZUSDT", "ETHUSDT", "BTCUSDT", "BNBBUSD", "TEST"]
    symbols_list = []
    for folder in folder_list:
        if folder.endswith(folder_end):
            symbols_list.append(folder)

    return symbols_list


def download_file(base_path, file_name, folder=None):
    download_path = "{}{}".format(base_path, file_name)
    save_path = get_destination_dir(os.path.join(base_path, file_name), folder)

    if os.path.exists(save_path):
        print("\nfile already exists! {}".format(save_path))
        return

    # make the directory
    if not os.path.exists(base_path):
        Path(get_destination_dir(base_path)).mkdir(parents=True, exist_ok=True)

    try:
        download_url = get_download_url(download_path)
        print(download_url)
        dl_file = urllib.request.urlopen(download_url)
        length = dl_file.getheader('content-length')
        if length:
            length = int(length)
            blocksize = max(4096, length // 100)

        with open(save_path, 'wb') as out_file:
            dl_progress = 0
            print("\nFile Download: {}".format(save_path))
            while True:
                buf = dl_file.read(blocksize)
                if not buf:
                    break
                dl_progress += len(buf)
                out_file.write(buf)
                done = int(50 * dl_progress / length)
                sys.stdout.write("\r[%s%s]" % ('#' * done, '.' * (50 - done)))
                sys.stdout.flush()

        return save_path

    except urllib.error.HTTPError:
        print("\nFile not found: {}".format(download_url))
        pass
    return None


def match_date_regex(arg_value, pat=re.compile(r'\d{4}-\d{2}-\d{2}')):
    if not pat.match(arg_value):
        raise ArgumentTypeError
    return arg_value


def get_path(trading_type, market_data_type, time_period, symbol, interval=None):
    trading_type_path = 'data/spot'
    if trading_type != 'spot':
        trading_type_path = f'data/futures/{trading_type}'
    if interval is not None:
        path = f'{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/{interval}/'
    else:
        path = f'{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/'
    return path


def get_parser(parser_type):
    parser = ArgumentParser(description=("This is a script to download historical {} data").format(parser_type),
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '-s', dest='symbols', nargs='+',
        help='Single symbol or multiple symbols separated by space')
    parser.add_argument(
        '-d', dest='date', nargs='+', type=match_date_regex,
        help='Date to download in [YYYY-MM-DD] format\nsingle date or multiple dates separated by space\ndownload from 2020-01-01 if no argument is parsed')
    parser.add_argument(
        '-folder_end', dest='folder_end', help='folder end')
    parser.add_argument(
        '-change_file', dest='change_file', default=".csv", choices=[".csv", ".pickle"],
        help='change file to .pickle')
    parser.add_argument(
        '-c', dest='checksum', default=0, type=int, choices=[0, 1],
        help='1 to download checksum file, default 0')
    parser.add_argument(
        '-t', dest='type', required=True, choices=TRADING_TYPE,
        help='Valid trading types: {}'.format(TRADING_TYPE))

    return parser
