from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import datetime
import json
import uuid
from logging import getLogger
logger = getLogger(__name__)


class MockCommentServiceRequestHandler(BaseHTTPRequestHandler):
    '''
    A handler for Comment Service POST requests.
    '''
    protocol = "HTTP/1.0"

    def _get_json(self):
        '''
        '''
        # Retrieve the POST or PUT data into a dict.
        # It should have been sent in json format
        length = int(self.headers.getheader('content-length'))
        data_string = self.rfile.read(length)
        return json.loads(data_string)

    def _return_failure(self, status=500, reason='Internal Server Error'):
        '''
        '''
        self.send_response(status, reason)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        return False

    def _handle(self, method):
        '''
        '''
        if method in ('POST', 'PUT'):
            try:
                post_dict = self._get_json()
            except Exception, e:
                pass
        else:
            post_dict = None

        logger.debug("Comment Service received {} request to path {}".format(
                    method, self.path))

        if not 'X-Edx-Api-Key' in self.headers:
            return self._return_failure(reason='Unauthorized')

        response = self.server._response_str
        # Log the response
        logger.debug("Comment Service: sending response %s" % json.dumps(response))

        # Send a response back to the client
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):
        '''
        Handle a POST request from the client
        Used by the APIs for comment threads, commentables, comments,
        subscriptions, commentables, users
        '''
        return self._handle('POST')

    def do_PUT(self):
        '''
        Handle a PUT request from the client
        Used by the APIs for comment threads, commentables, comments,
        subscriptions, commentables, users
        '''
        return self._handle('PUT')

    def do_GET(self):
        '''
        Handle a GET request from the client
        '''
        return self._handle('GET')


class MockCommentServiceServer(HTTPServer):
    '''
    A mock Comment Service server that responds
    to POST requests to localhost.
    '''
    def __init__(self, port_num,
                 response={'username': 'new', 'external_id': 1}):
        '''
        Initialize the mock Comment Service server instance.
        *port_num* is the localhost port to listen to
        *response* is a dictionary that will be JSON-serialized
            and sent in response to comment service requests.
        '''
        self._response_str = json.dumps(response)

        handler = MockCommentServiceRequestHandler
        address = ('', port_num)
        HTTPServer.__init__(self, address, handler)

    def shutdown(self):
        '''
        Stop the server and free up the port
        '''
        # First call superclass shutdown()
        HTTPServer.shutdown(self)

        # We also need to manually close the socket
        self.socket.close()
