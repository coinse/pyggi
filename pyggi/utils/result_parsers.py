class TimeoutError(Exception):
    pass

class InvalidPatchError(Exception):
    pass

def standard_result_parser(stdout: str, stderr: str):
    try:
        return float(stdout.strip())
    except:
        raise InvalidPatchError