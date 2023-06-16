#%%

import aiohttp
import logging

from bs4 import BeautifulSoup

#%%

class Film_Checker:
    """this class is used to check if a film is available in a cinema
    """
    def __init__(self, url) -> None:
        self.url = url

    async def get_website(self) -> BeautifulSoup:
        """this function fetches the website content and returns a BeautifulSoup object

        Returns
        -------
        BeautifulSoup
            the website content as a BeautifulSoup object
        """

        try:

            async with aiohttp.ClientSession() as session:

                async with session.get(self.url) as response:
                    html_content = await response.text()
                    self.soup = BeautifulSoup(html_content, "html.parser")

        except Exception as e:
            logging.error(f'Error fetching website content: {e}')

    def check_availability(self) -> bool:
        """this function checks if a film is available in a cinema
        returns True if the film is available, False if not

        Returns
        -------
        bool
        """

        try:
            return ( self.soup.find(class_='row gwfilmdb-film-schedule') is not None ) or ( self.soup.find(class_='gwfilmdb-film-schedule') is not None )

        except Exception as e:
            logging.error(f'Error checking availability in the html content: {e}')
            return False

    def check_imax_3d_ov(self) -> bool:
        """this function checks if a film is available in IMAX 3D OV in a cinema
        returns True if the film is available, False if not

        Returns
        -------
        bool
        """

        try:
            return self.soup.find('a', {'title': 'Spielplan der IMAX 3D OV-Vorstellungen anzeigen'}) is not None

        except Exception as e:
            logging.error(f'Error checking IMAX 3D OV in the html content: {e}')
            return False

    def check_imax_ov(self) -> bool:
        """this function checks if a film is available in IMAX OV in a cinema
        returns True if the film is available, False if not

        Returns
        -------
        bool
        """

        try:
            return self.soup.find('a', {'title': 'Spielplan der IMAX OV-Vorstellungen anzeigen'}) is not None

        except Exception as e:
            logging.error(f'Error checking IMAX OV in the html content: {e}')
            return False

    def check_hd_ov(self) -> bool:
        """this function checks if a film is available in HD OV in a cinema
        returns True if the film is available, False if not

        Returns
        -------
        bool
        """

        try:
            return self.soup.find('a', {'title': 'Spielplan der HD OV-Vorstellungen anzeigen'}) is not None

        except Exception as e:
            logging.error(f'Error checking HD OV in the html content: {e}')
            return False
