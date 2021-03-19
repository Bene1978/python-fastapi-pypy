from inspect import Parameter, Signature
import azure.functions as az_functions
import ujson as json


class FastApiWrapper:
    """
    Converts a FastAPI route into a "function object" that Azure Functions
    worker will use to call incoming HTTP requests.
    """

    def __init__(self, f) -> None:
        self.f = f

    def __call__(self, req: az_functions.HttpRequest) -> az_functions.HttpResponse:
        kwargs = req.route_params
        response = self.f(**kwargs)

        if isinstance(response, dict):
            response = json.dumps(response)

        return az_functions.HttpResponse(
            response,
            status_code=200,
        )

    @property
    def __annotations__(self):
        # TODO : Be clever about the annotations based on FastAPI specs
        return self.f.__annotations__

    @property
    def __signature__(self):
        """
        Pretend this function only has 1 arg(req) but at calltime it will leverage
        the request object.
        """
        return Signature(parameters=(Parameter(name="req", kind=1),))


def as_function(f):
    return FastApiWrapper(f)
