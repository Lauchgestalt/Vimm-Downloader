# Vimm ROM Downloader

This is a simple python script you can use, if you want to download whole system collections off Vimm's Vault.
Simply edit the scraper.py to match your use case:

- Add all the systems you want to the systems array (Use the short form used on vimm. Simply open the category in a browser and grab the short form from the URL)
- Add all the filters you want **except &p, &action, &system and &section** and make sure the filter string starts with an & (you can also simply apply the filters in your browser and then copy all the necessary parameters from the URL)

That's it.

The script will now get all the ROM files that match your search criteria (looping over systems and categories (#-Z)) and download them to a subfolder called rom.