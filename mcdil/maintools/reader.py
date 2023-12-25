import warnings
from pathlib import Path

import requests
from yarl import URL

from ..constants import CODE_CACHE_TYPE
from ..errors import SourceCodeFetchFailed


def read(
    source: str,
    base_path: Path | URL | None = None,
    code_cache: CODE_CACHE_TYPE | None = None,
) -> tuple[str, Path | URL]:
    """
    Get the source code and absolute path of the code then return it.
    When the compilation starts, the compiler will call this function
    whenever it encounters another import statement.
    You can use local file or web page as source of the code,
    however using too many web sources could be slow,
    because we don't know how many recursively chained web import will come
    before we access the code, therefore be careful.
    """

    code_cache = code_cache or {}

    if isinstance(source, str):
        source = source.strip()

    try:
        # Try file
        target_file_path: Path = (
            (base_path / source) if isinstance(base_path, Path) else Path(source)
        )
        try:
            # If file path is already available in cache, reuse it
            target_file_path = target_file_path.absolute()
            if target_file_path in code_cache:
                return code_cache[target_file_path], target_file_path

            # Direct gather
            with open(target_file_path, "r") as source_file:
                return source_file.read(), target_file_path

        except FileNotFoundError:
            warnings.warn(
                "Tried to open file at %s but failed to find the file."
                % (target_file_path,)
            )

        assert not isinstance(
            source, Path
        ), "`source` should be non-Path type if failed to fetch from file"

        # Try network
        if (
            source.startswith("http")
            or source.startswith("https")
            or isinstance(base_path, URL)
        ):
            target_network_path: URL = (
                base_path / source if isinstance(base_path, URL) else URL(source)
            )

            # If URL is already available in cache, reuse it
            if target_network_path in code_cache:
                return code_cache[target_network_path], target_network_path

            # Direct gather
            response = requests.get(str(target_network_path))
            if response.status_code // 100 == 2:
                return response.text, target_network_path

        raise SourceCodeFetchFailed(source)

    # Throw an exception if there is unintended error
    except Exception as err:
        raise SourceCodeFetchFailed(source, err).with_traceback(err.__traceback__)
