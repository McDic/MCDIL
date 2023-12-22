from pathlib import Path

import requests

from .errors import SourceCodeFetchFailed


def get_code(source: Path | str, base_path: Path | None = None) -> str:
    """
    Get the source code and return.
    When the compilation starts, the compiler will call this function
    whenever it encounters another import statement.
    You can use local file or web page as source of the code,
    however using too many web sources could be slow,
    because we don't know how many recursively chained web import will come
    before we access the code, therefore be careful.
    """

    try:
        # Try file
        target_file_path: Path = (
            base_path / source if isinstance(base_path, Path) else Path(source)
        )
        try:
            with open(target_file_path, "r") as source_file:
                return source_file.read()
        except FileNotFoundError:
            pass

        assert isinstance(
            source, str
        ), "`source` should be str type if failed to fetch from file"

        # Try network
        try:
            response = requests.get(source)
            if response.status_code // 100 == 2:
                return response.text
        except requests.ConnectionError as err:
            raise err

    # Throw an exception if there is unintended error
    except Exception as err:
        raise SourceCodeFetchFailed(
            'Failed to fetch source code from "%s" by error <%s>' % (source, err)
        ).with_traceback(err.__traceback__)

    # Throw an exception anyway
    finally:
        raise SourceCodeFetchFailed(
            'Failed to fetch source code from "%s" with unknown reason' % (source,)
        )
