from pgactivity import runtime


def ActivityMiddleware(get_response):
    """
    Annotates the url/method in the pgactivity context.
    """

    def middleware(request):
        with runtime.context(url=request.path, method=request.method):
            return get_response(request)

    return middleware
