# mfp_parameters.py is connected with mfp.py
# file for storing parameters, empty values will be omitted
# it's set to py extension rather then txt only to have color syntax highlight
{
                          # example  "dwhaley@lagoon.org",
    "mfpusername"                  : "",
    
    "mfppassword"                  : "",

    # in what interval in seconds program to recheck for new command file commands.txt integer
    "command_wait"                 :  1,
    
    # timeout for openning web page in seconds, integer
    "timeout"                      : 10,
    
    # due various firefox and selenium versions, using geckodriver is recommended
    # ie. set value to integer 1 (with 0 selenium will try to work with default firefox browser)
    # newest geckodriver executable can be downloaded from https://github.com/mozilla/geckodriver/releases
    # unpacked and placed in some directory. 1 is True, value should be 1 as integer
    "usegecko"                     : 1,
    # on right set full path to geckodriver exectuable (not directory only)
    # assuming that user on your droplet will be called mfp, project files placed in mfp directory
    # and created subdirectory called browserdir and geckodriver placed there (more instructions in README.md file)
    "geckodriverexcecutablePath"   : "/home/mfp/mfp/browserdir/geckodriver",
    
    # using firefox profile is needed for their scrapping check
    # Remember linkedin login in that profile, that way in script login will be skipped.
    # You can work with firefox profiles starting firefox with: firefox -P
    # http://ccm.net/faq/1934-firefox-finding-the-profile-folder
    # in next line set path to directory with firefox profile (not ending slash)
    "ffProfilePath"                : "/home/mfp/mfp/browserdir",
    
    # integer for firefox window Width and Height
    "ffWidth"                      : 1280,
    "ffHeight"                     :  800

}
