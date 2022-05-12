import uvicorn
import main
from multiprocessing import Process
from time import sleep


app_process = None


def run():
    uvicorn.run(main.app, port=8888)


def before_scenario(context, tag):
    global app_process
    print('Starting uvicorn...')
    app_process = Process(target=run, daemon=True)
    app_process.start()
    sleep(0.25)
    print('Started uvicorn')
    # context.server_process = Popen(
    #     f'uvicorn main:app --host 127.0.0.1 --port 8888',
    #     shell=True,
    #     stdout=PIPE,
    #     stderr=PIPE,
    #     bufsize=-1)
    # sleep(0.5)
    # assert context.server_process.returncode is None
    # print(f'Started uvicorn, pid: {context.server_process.pid}')


def after_scenario(context, tag):
    print('Stopping uvicorn...')
    app_process.kill()
    sleep(0.25)
    print('Stopped uvicorn')
    # if context.server_process is not None and context.server_process.returncode is None:
    #     Popen(f"kill {context.server_process.pid}", shell=True).wait(1)
