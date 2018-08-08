import os

try:
    import pgi

    pgi.install_as_gi()
    pgi.require_version('Notify', '0.7')
    from pgi.repository import Notify
    linux = True
except ImportError:
    pgi = None

if not pgi:
    try:
        import win10toast as windows

    except ImportError:
        windows = None


if pgi:
    def main():
        print('Linux notification.')
elif windows:
    def main():
        print('Windows notification.')
        toaster = windows.ToastNotifier()
        toaster.show_toast('Completed', 'HIGH20',
                           icon_path=os.path.abspath(os.path.join(__file__, '..', '..', 'warning.ico')),
                           duration=3)
else:
    raise NotImplementedError('Notification module not implemented in this OS')


if __name__ == '__main__':
    main()
