import sys
import asyncio

messages = asyncio.Queue()


async def store_it():
    rp = open('temp.txt', 'a')
    try:
        while True:
            msg = messages.get()
            if not msg:
                break
            rp.write(msg)
    except asyncio.CancelledError:
        rp.close()


if __name__ == '__main__':
    if sys.argv[1] == 'start':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(store_it)
    elif sys.argv[1] == 'stop':
        messages.put(None)
        loop = asyncio.get_event_loop()
        loop.close()
    elif sys.argv[1] == 'event':
        messages.put(sys.argv[1] + '\n')
