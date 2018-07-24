class Event(object):

    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except KeyError:
            print('Could not find the handler to unhandle it')
        return self

    def __call__(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

    def __len__(self):
        return len(self.handlers)

    def __str__(self):
        handler_names = []
        for handler in self.handlers:
            handler_names.append(handler.__name__)
        return str(handler_names)

    def __repr__(self):
        return str(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle


class MockFileWatcher:
    def __init__(self):
        self.file_changed = Event()

    def watch_files(self):
        source_path = "foo"
        self.file_changed(source_path)


def log_file_change(source_path):
    print("%r changed." % source_path)


def log_file_change2(source_path):
    print("%r changed!" % source_path)


if __name__ == '__main__':
    watcher = MockFileWatcher()
    watcher.file_changed += log_file_change2
    watcher.file_changed += log_file_change
    watcher.file_changed -= log_file_change2
    print(repr(watcher.file_changed))
    print(watcher.file_changed)

    # watcher.watch_files()
