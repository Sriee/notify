import sys
import asyncio

messages = asyncio.Queue()


async def store_it():
    rp = open('temp.txt', 'a')
    try:
        while True:
            msg = await messages.get()
            if not msg:
                break
            rp.write(msg)
    except asyncio.CancelledError:
        rp.close()

loop = asyncio.get_event_loop()


if __name__ == '__main__':
    if sys.argv[1] == 'start':
        loop.run_until_complete(store_it())
    elif sys.argv[1] == 'stop':
        print(loop.is_running(), 'stop')
        messages.put(None)
        loop.close()
    elif sys.argv[1] == 'event':
        print(loop.is_running(), 'event')
        print(asyncio.Task.all_tasks())
        messages.put(sys.argv[2] + '\n')
    else:
        print('Supported command { stop | event }')
