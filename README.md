Url: https://data.binance.vision/?prefix=data/futures/um/daily/aggTrades/ 

### 参数说明: 
-t	Market type: spot, um (USD-M Futures), cm (COIN-M Futures) 必传参数  
-d	下载指定日期的文件, eg: 2024-01-01 必传参数  
-folder_end	现在目录以什么结尾 eg: USDT  
-c	1 下载 checksum 文件 0 不下载  
-change_file 修改源文件为什么后缀结尾的文件 eg: [".pickle"]  

### Example
e.g 下载所有以USDT结尾的文件夹中2024年1月1日的zip压缩文件数据。对数据进行解压及完整性校验，并将其转换为.pickle文件进行存储  
`python3 getData.py -t um -d 2024-01-01 -c 1 -folder_end USDT -change_file .pickle`

### 目录说明:
build: 对源代码进行加密加密文件  
data: 下载文件目录  
getData.py : 下载源文件  
until.py: common 文件  
