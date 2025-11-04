from multiprocessing import cpu_count

bind = "127.0.0.1:82"

workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/ihris-reporting-fastapi/log/access_log'
errorlog =  '/home/ihris-reporting-fastapi/log/error_log'