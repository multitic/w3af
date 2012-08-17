'''
full_width_encode.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

from core.controllers.basePlugin.baseEvasionPlugin import baseEvasionPlugin
from core.controllers.w3afException import w3afException
from core.data.url.HTTPRequest import HTTPRequest as HTTPRequest
from core.data.parsers.urlParser import parse_qs

# options
from core.data.options.option import option
from core.data.options.optionList import optionList

import urllib


class full_width_encode(baseEvasionPlugin):
    '''
    Evade detection using full width encoding.
    
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''

    def __init__(self):
        baseEvasionPlugin.__init__(self)

    def modifyRequest(self, request ):
        '''
        Mangles the request
        
        @parameter request: HTTPRequest instance that is going to be modified by the evasion plugin
        @return: The modified request

        >>> from core.data.parsers.urlParser import url_object
        >>> fwe = full_width_encode()
        
        >>> u = url_object('http://www.w3af.com/')
        >>> r = HTTPRequest( u )
        >>> fwe.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/'

        >>> u = url_object('http://www.w3af.com/hola-mundo')
        >>> r = HTTPRequest( u )
        >>> fwe.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/%uFF48%uFF4f%uFF4c%uFF41%uFF0d%uFF4d%uFF55%uFF4e%uFF44%uFF4f'

        >>> u = url_object('http://www.w3af.com/hola-mundo')
        >>> r = HTTPRequest( u )
        >>> fwe.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/%uFF48%uFF4f%uFF4c%uFF41%uFF0d%uFF4d%uFF55%uFF4e%uFF44%uFF4f'
        >>> #
        >>> #    The plugins should not modify the original request
        >>> #
        >>> u.url_string
        u'http://www.w3af.com/hola-mundo'
        '''
        # This is a test URL
        # http://172.16.1.132/index.asp?q=%uFF1Cscript%3Ealert(%22Hello%22)%3C/script%3E
        # This is the content of index.asp :
        # <%=Request.QueryString("q")%>
        
        # First we mangle the URL        
        path = request.url_object.getPath()
        path = self._mutate( path )
        
        # Now we mangle the postdata
        data = request.get_data()
        if data:
            
            try:
                # Only mangle the postdata if it is a url encoded string
                parse_qs( data )
            except:
                pass
            else:
                # We get here only if the parsing was successful
                data = self._mutate( data )            
        
        # Finally, we set all the mutants to the request in order to return it
        new_url = request.url_object.copy()
        new_url.setPath( path )
        
        new_req = HTTPRequest( new_url , data, request.headers, 
                               request.get_origin_req_host() )
        
        return new_req
    
    def _mutate( self, to_mutate ):
        to_mutate = urllib.unquote( to_mutate )
        mutant = ''
        for char in to_mutate:
            if char not in ['?', '/', '&', '\\', '=', '%', '+']:
                # The "- 0x20" was taken from UFF00.pdf
                char = "%%uFF%02x" % ( ord(char) - 0x20 )
            mutant += char
        return mutant

    def get_options( self ):
        '''
        @return: A list of option objects for this plugin.
        '''    
        ol = optionList()
        return ol

    def set_options( self, OptionList ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of get_options().
        
        @parameter OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        pass
        
    def getPluginDeps( self ):
        '''
        @return: A list with the names of the plugins that should be run before the
        current one.
        '''        
        return []

    def getPriority( self ):
        '''
        This function is called when sorting evasion plugins.
        Each evasion plugin should implement this.
        
        @return: An integer specifying the priority. 0 is run first, 100 last.
        '''
        return 50
    
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This evasion plugin does full width encoding as described here:
            - http://www.kb.cert.org/vuls/id/739224
        
        Example:
            Input:      '/bar/foo.asp'
            Output :    '/b%uFF61r/%uFF66oo.asp'
        '''
