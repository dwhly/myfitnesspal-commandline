## Tired of their user interface? Use MFP from the command line or a chat interface (XMPP, etc) 
myfitnesspal automation using jabber/xmpp  
  
Author: Dan Whaley https://hypothes.is  
Author: Aleksandar Josifoski https://about.me/josifsk  
  
Commands in terminal are recognizible with $ prefix  
  
----------------------  
First things to do:  
* If you have connection to myfitnesspal via facebook, you'll need to disconnect and make login credentials  
  as described here:   https://myfitnesspal.desk.com/customer/portal/articles/888996-how-do-i-unlink-my-myfitnesspal-and-facebook-accounts-  
  
* You'll need to create (if not having) 3 jabber accounts, one will be used by keep.py script, other for laptop/desktop IM messenger, third for mobile (although jabber supports synchronization of messages, more stable will be using own jabber ID for mobile.  
  
* Next step is to make 3 jabber accounts to mutually (both directions) authorize each other. You can do that using some xmpp client. After that remember, server jabber account should be logged only via keep.py, disconnect it from laptop messenger.  
  
* Update mfp_parameters.py file with your mfp username and password. Later you will need 2 subdirectories in main directory (let called it mfp on server) browserdir and responses. browserdir will be connected with headless firefox using geckodriver, responses directory will be used for main python program called mfp.py to send msgs to keep.py (which is xmpp 2 directional client for receiving/sending messages) with which you will communicate! (Directories defined in parameters file should match prepared on server) 
  
* In keep.py fill server xmpp (that is CLIENT_JID = ), set password for it (in CLIENT_PASSWORD = ) and in (AUTHORIZED_JIDS = ) you can set your personal xmpp accounts. Also specify dir_in variable with correct path, where project files are placed.  

* In mfp.py enter correct directory path for dir_in variable (should be same as dir_in in keep.py).
  
----------------------  
## Server (instructions are related to digitalocean)  
  
# At local/home computer generating public/private ssh key pair  
in terminal  
$ ssh-keygen -t rsa  
* it will ask for filename where keys to be stored  
* notice where files will be saved, for example if filename is dan  
  command will generate two files dan & dan.pub where dan is file with private, dan.pub with public key  
* you can ommit passhprase simply with hitting enter when asked. If you prefer you can set passphrase, remember passwords generated on server per user are not related with this passphrase.  
  
# Creating ubuntu 16.04 droplet (on digitalocean)  
in ssh field you should copy value of dan.pub (if public key is in dan.pub)  
you can take contents of file with cat command  
$ cat dan.pub (on your laptop, if you are navigated in console at correct directory where key files are)  
Navigating in console is using with cd command  
  
Select text inside with right click then copy and paste it in field  
  
For ssh name on digitalocean enter for example ubuntussh (not relevant)  
  
# connection via ssh  
$ ssh -vvv -i dan root@your-digitalocean-droplet-ip  
Above command assumes that your key is called dan, that you are navigated in terminal to directory where your private key is placed. (on your laptop)  
  
You should be now connected via terminal to server via ssh  
  
First command on newly created dropled (you are connected via ssh)  
$ sudo apt update  
  
Next following instructions from here  
https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04  
(Assuming that you are connected via ssh to root)  
* Create a New User called mfp  
$ adduser mfp  (and remember/write somewhere entered password)  
* Add root privileges to user mfp  
$ usermod -aG sudo mfp  
$ su - mfp  
$ mkdir ~/.ssh  
$ chmod 700 ~/.ssh  
$ nano ~/.ssh/authorized_keys  
* in nano paste your public key contents (as above for root with cat dan.pub, same key is fine but now for user mfp avoiding ssh to root), this way you  will have ssh access to droplet via username mfp  
* Hit Ctrl + X and save file  
* Now restrict the permissions of the authorized_keys file with this command:  
$ chmod 600 ~/.ssh/authorized_keys  
$ exit  
  
close terminal window, reopen it, test ssh connection using user (in this case mfp (not root) via command  
$ ssh -vvv -i dan mfp@your-ip (mfp is user, dan is name of file with your private key (do not forget to be navigated previously via cd command to directory where private key is, project source file should be also placed there))  
  
Adjusting server time where project will be uploaded (not mfp site) to your local timezone  
https://www.digitalocean.com/community/tutorials/how-to-set-up-time-synchronization-on-ubuntu-16-04  
Briefly  
Find your timezone with  
$ timedatectl list-timezones  (then use pageup/down to scroll, let say it's America/Los_Angeles)  
then  
$ sudo timedatectl set-timezone America/Los_Angeles  
(This way server time will be adjusted to your local time which is important for synchronization with mfp site)  
  
* If you travel to other time zone do not forget to execute sudo timedatectl set-timezone newtimezone  
  
----------------------  
# Create mfp directory for user mfp  
After successful login via ssh  
$ mkdir mfp  
$ cd mfp  
(stay there in mfp directory for following installations)  
----------------------  
# Installation  dependencies  
keep.py is using python2.7  
mfp.py is using python3+, default 3.5 on digitalocean is fine  
  
$ export LC_ALL="en_US.UTF-8"  
$ export LC_CTYPE="en_US.UTF-8"  
$ sudo dpkg-reconfigure locales  
(choose from left side (using arrow keys) en_US.UTF-8 UTF-8 (hit space) and navigating with tab key go to ok and hit space)  
  
$ sudo apt update  
$ sudo apt install python2.7  
$ sudo apt install python3-pip    
$ sudo apt install python-pip  
$ sudo /usr/bin/pip3 install --upgrade pip  
$ sudo pip3 install selenium BeautifulSoup4   
  
* installing (updated) xmmppy library  
$ sudo pip2 install git+https://github.com/ArchipelProject/xmpppy  
  
* firefox is set to do selenium tasks, using xvfb-run command to start headless (on server headless is MUST)  
$ sudo apt install firefox xvfb libXfont Xorg  
* geckodriver  
$ wget https://github.com/mozilla/geckodriver/releases/download/v0.20.1/geckodriver-v0.20.1-linux64.tar.gz  
(or you can check for new geckodriver release on https://github.com/mozilla/geckodriver/releases/download/)  
if newer change above wget command, check that is for linux64)  
* unpacking archive  
$ tar -xzfv geckodriver-v0.20.1-linux64.tar.gz  
  
* create responses and browserdir subdirectories  
$ mkdir responses  
$ mkdir browserdir  
  
* move geckodriver to browserdir directory (should be compatible with variable geckodriverexcecutablePath in parameters file)  
$ mv geckodriver /home/mfp/mfp/browserdir/geckodriver  
  
----------------------  
You will need some basic ssh and sftp knowledge. You will use sftp to place project files on server.  
https://www.digitalocean.com/community/tutorials/how-to-use-sftp-to-securely-transfer-files-with-a-remote-server  
https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys  
  
sftp Briefly  
From home terminal (navigated to directory where project and key files are)  
You are logging to user same as ssh command, only first string is sftp  
For example  
$ sftp -vvv -i dan mfp@your-ip  
Navigate to directory prepared for project files, let's called it mfp (although user on server is also mfp)  
$ cd /home/mfp/mfp
$ put * (this command will place all files in your local current directory at /home/mfp/mfp/  
You can place only some files for example  
$ put mfp.py (will upload only mfp.py in /home/mfp/mfp/)  
Basically from sftp you will need only this brief explanations, to upload files on server  
You can check that everything is fine uploaded via other ssh terminal window with ls command.  
  
----------------------  
Starting project (&)  
(Assuming that you are ssh logged and navigated to mfp directory)  
$ at now  
at> python keep.py (hit Enter then Ctrl + d)  
$ at now  
at> xvfb-run python3 mfp.py (hit Enter then Ctrl + d)  
  
* checking that python scripts are running  
$ ps aux | grep python  
  
* In few moments you should have established xmpp communication with server jabber id via your local client, and you can enter commands.  
  
----------------------  
ssh faqs (Briefly)  
Using ssh assumes some basic knowledge of linux command line.  
  
How to edit/change something in project files on server?  
You can use vim or nano editors.  
  
Does project create log file?  
Yes, it's defined in mfp_log.txt.  
You can tail it with  
$ tail -200 mfp_log.txt (this will list last 200 lines in log)  
  
Can I use project at home computer, not on server?  
Yes. Installation dependecies are same. Update mfp_parameters.py with needed info.  
However, xvfb is compatible on linux systems, if you have Mac or using Windows, you will need to start project with visible firefox, or to modify project and implement phantomjs or something.  
  
Recommended command for entering food data:  
m [or match]. See help for more  
  
----------------------  
Commands for using project via xmpp client.  
Is project is started on server?  
  
command you should memorize is help  
it will generate this (as response xmpp msg)  
  
help  
  
sm [or searchmap] (Search in mapping file example: sm kiwi will find all lines where kiwi is inside line)  
  
lqr [or listquantityrelations] (List quantities relations. This command will list quantities_abbrev.txt file if using match command with quantities for conversions.)  
  
n [or note] words (Append note example: n some my note)  
  
sn [or searchnotes] term (Search in notes term)  
  
rnl [or removenoteslines] (Remove notes lines Example: rnl 3, 5, 8 those lines will be removed. This command is for using after searching notes with sn)  
  
map (Adding manually new mapping example: map driedkiwi : Dried Kiwi, 6 Slices, 46 calories [Must have : for separator between key and name in db])  
  
dbmap (Adding new mapping when previous command was sdb example: dbmap  peas : 008 [where 008 is 8.th by sdb listed food]. Later you can use fm command to add food )  
  
fm [or frommap] (Adding food via map in today mfp list example: fm driedkiwi 1 c [where driedkiwi is already present as key in mappings], 1 c means 1 cup. For now fm command is dependend on quantity input, also keys have to be described in one word)  
  
cs [or status] (Calories status)  
  
lt [or listtoday] (List today entered foods)  
  
undo (Remove last added food, you can remove more foods with using more then once undo)  
  
s [or sdb or search] words (Search in db words)  
  
st [or searchtabs] words (search in recent/frequent/myfoods/meals/recipes words. Example: searchtabs kiwi raw)  
  
more [or next] (After searching in db, you can use this command to show you next 10 results)  
  
prev (For showing 10 previous results from search command)  
  
m [or match] (Adding food Example: m banana, raw @ 15 oz [It will seek in recent/frequent/myfoods/meals/recipes/db. In this case program will try to find conversion for metric value from allowed set by given food. If metric is omitted "Example: m banana raw @ 2" it will process first metric value from their allowed set for found food with 2 servings. If used without @ symbol quantity will be 1 serving for first metric value from allowed set for found food "Example: m banana raw])  
  
allowed_commands = ['help', 'm', 'match', 'lt', 'listtoday', 'sn', 'searchnotes', 'sm', 'searchmap','cs', 'status', 'n', 'note', 'map', 'dbmap', 'fm', 'frommap', 'undo', 'lqr', 'listquantityrelations', 'rnl', 'removenoteslines', 's', 'sdb', 'search', 'st', 'searchtabs', 'next', 'more', 'prev']  

----------------------  
Final notes

Scripts will work continuously, if for some reason restarting droplet will be needed you will have to start them once again. (&)  

If problem in xmpp messaging happen, problem may be eventually localised at your xmpp provider. Remember to preiously mutually authorize xmpp accounts, and do not set active at home server xmpp account. keep.py will drive it.

mfp.py is accepting command.txt file (which is generated by keep.py), that means you can use ssh and command line for everything without jabber implementation. Simply you can use echo command like
echo "m bananas raw @ 2" > command.txt

