import os
import sys

from until import download_file, get_all_symbols, get_parser, get_path, unzip_file, run_linux_command
import pandas as pd
import pickle
from concurrent.futures import ThreadPoolExecutor


def download_daily_aggTrades(trading_type, symbol, date, checksum=None, change_file=".pickle"):
    print(f"{symbol} task is running")
    path = get_path(trading_type, "aggTrades", "daily", symbol)
    file_name = "{}-aggTrades-{}.zip".format(symbol.upper(), date)
    zip_path = download_file(path, file_name)

    # 解压 zip
    dest_path = unzip_file(zip_path)

    if checksum == 1:
        checksum_path = get_path(trading_type, "aggTrades", "daily", symbol)
        checksum_file_name = "{}-aggTrades-{}.zip.CHECKSUM".format(symbol.upper(), date)
        checksum_file_path = download_file(checksum_path, checksum_file_name)

        result = run_linux_command(f"sha256sum -c {checksum_file_name}", cwd=os.path.dirname(checksum_file_path))
        if "成功" in result:
            name, suffix = os.path.splitext(dest_path)
            # to .pickle 文件
            df = pd.read_csv(dest_path)
            with open(f'{name}{change_file}', 'wb') as handle:
                pickle.dump(df, handle)
            print("verify success")

        else:
            print("verify fail")


if __name__ == "__main__":
    parser = get_parser('aggTrades')
    args = parser.parse_args(sys.argv[1:])

    if not args.symbols:
        print("fetching all symbols from exchange")
        symbols = get_all_symbols(args.type, args.folder_end)
        num_symbols = len(symbols)
    else:
        symbols = args.symbols
        num_symbols = len(symbols)

    print("fetching {} symbols from exchange".format(num_symbols))

    pool = ThreadPoolExecutor(max_workers=5)
    for symbol in symbols:
        pool.submit(download_daily_aggTrades, args.type, symbol, args.date[0], args.checksum, args.change_file)

    pool.shutdown()
