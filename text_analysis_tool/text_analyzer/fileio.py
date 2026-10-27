"""File reading and report saving.

Every failure is converted into a :class:`TextFileError` carrying a message
that is safe to show to the user.  The menu catches that one exception type,
prints the message and carries on, so a bad path can never crash the program
(assignment requirement 1 and the "Missing file" test case).
"""

import os

REPORT_FILENAME = "analysis_report.txt"
MAX_FILE_BYTES = 10 * 1024 * 1024       # refuse files above 10 MB


class TextFileError(Exception):
    """A file could not be read or written. str(error) is user-friendly."""


def clean_path(raw_path: str) -> str:
    """Tidy a path typed or drag-and-dropped into the terminal.

    Windows wraps dropped paths in double quotes; strip those and any stray
    spaces so "  \"C:\\\\my notes\\\\a.txt\" " works.
    """
    return raw_path.strip().strip('"').strip("'").strip()


def read_text_file(raw_path: str) -> str:
    """Read a UTF-8 text file and return its contents.

    Raises TextFileError (never any other error) when the path is blank, the
    file is missing, is a folder, cannot be opened, is too large, or is not
    valid UTF-8 text.
    """
    path = clean_path(raw_path)
    if not path:
        raise TextFileError("No file path was entered.")

    try:
        if os.path.getsize(path) > MAX_FILE_BYTES:
            raise TextFileError(
                "File is too large (limit is %d MB)." % (MAX_FILE_BYTES // (1024 * 1024))
            )
        # "utf-8-sig" silently removes the invisible BOM that Windows Notepad
        # adds to some files.
        with open(path, "r", encoding="utf-8-sig") as handle:
            return handle.read()
    except FileNotFoundError as error:
        raise TextFileError("File not found: %s" % path) from error
    except IsADirectoryError as error:
        raise TextFileError("That path is a folder, not a file: %s" % path) from error
    except PermissionError as error:
        raise TextFileError("Permission denied: %s" % path) from error
    except UnicodeDecodeError as error:
        raise TextFileError(
            "That file is not plain UTF-8 text, so it cannot be analysed."
        ) from error
    except OSError as error:
        raise TextFileError(
            "Could not read the file (%s)." % (error.strerror or "unknown error")
        ) from error


def save_report(content: str, path: str = REPORT_FILENAME) -> str:
    """Write *content* to *path* and return the absolute path written.

    The text is first written to a temporary file and then moved into place,
    so a failure part-way through can never leave a half-written report.
    """
    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_path, path)     # atomic on Windows, macOS and Linux
    except OSError as error:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise TextFileError(
            "Could not save the report (%s)." % (error.strerror or "unknown error")
        ) from error
    return os.path.abspath(path)
