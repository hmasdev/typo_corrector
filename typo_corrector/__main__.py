from logging import basicConfig, DEBUG, INFO  # noqa
from .main import main


if __name__ == '__main__':
    basicConfig(level=INFO)
    main()
