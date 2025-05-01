class CookiesToRequestHeader:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization

    def __call__(self, request):
        # Get the access token from the cookies
        access_token = request.COOKIES.get('access_token')

        # If the token is found, set it in the request headers
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'

        # Get the response from the view
        response = self.get_response(request)
        return response